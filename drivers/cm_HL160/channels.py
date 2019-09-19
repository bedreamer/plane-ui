# -*- coding: utf8 -*-
import struct
import logging
import socket
# import serial.urlhandler.protocol_socket as serial
# import modbus


def calculate_crc16(data):
    """Calculate CRC16 using the given table.
    `data`      - data for calculating CRC, must be bytes
    Return calculated value of CRC
    """
    crc = 0xffff
    for byte in data:
        crc = crc ^ byte
        for i in range(8):
            x = crc & 1
            crc = crc >> 1
            crc = crc & 0x7fff
            if x:
                crc = crc ^ 0xa001
    return crc & 0xffff


class ModbusChannelBasic(object):
    """
    MODBUS基本通道
    """

    def open(self):
        """
        打开MODBUS通道
        :return: True if success False else
        """
        raise NotImplementedError

    def close(self):
        """
        关闭MODBUS通道
        :return: True if success False else
        """
        raise NotImplementedError

    @classmethod
    def read_multiple_register(cls, dev_address, function_code, starting_address, quantity_coils):
        return [struct.pack("B", dev_address), struct.pack("B", function_code),
                struct.pack(">H", starting_address), struct.pack(">H", quantity_coils)]

    @classmethod
    def read_coils(cls, dev_address, starting_address, quantity_coils):
        return cls.read_multiple_register(dev_address, 0x01, starting_address, quantity_coils)

    @classmethod
    def read_discrete_inputs(cls, dev_address, starting_address, quantity_of_inputs):
        return cls.read_multiple_register(dev_address, 0x02, starting_address, quantity_of_inputs)

    @classmethod
    def read_holding_registers(cls, dev_address, starting_address, quantity_of_registers):
        return cls.read_multiple_register(dev_address, 0x03, starting_address, quantity_of_registers)

    @classmethod
    def read_input_registers(cls, dev_address, starting_address, quantity_of_input_registers):
        return cls.read_multiple_register(dev_address, 0x04, starting_address, quantity_of_input_registers)

    @classmethod
    def write_single_coil(cls, dev_address, output_address, output_value):
        return [struct.pack("B", dev_address), b'\x05',
                struct.pack(">H", output_address), struct.pack(">H", output_value)]

    @classmethod
    def write_single_register(cls, dev_address, register_address, register_value):
        return [struct.pack("B", dev_address), b'\x06',
                struct.pack(">H", register_address), struct.pack(">H", register_value)]

    def x03_read(self, dev_address, reg_address):
        """
        读单个寄存器
        :param dev_address: 设备地址
        :param reg_address: 寄存器地址
        :return: <modbus.ModbusResponse object>
        """
        raise NotImplementedError

    def x06_write(self, dev_address, reg_address, reg_bin_value):
        """
        写单个寄存器
        :param dev_address: 设备地址
        :param reg_address: 寄存器地址
        :param reg_bin_value: 寄存器值
        :return: <modbus.ModbusResponse object>
        """
        raise NotImplementedError


class TCPModbusChannel(ModbusChannelBasic):
    """
    TCP版的MODBUS通道
    """
    pass


class Serial2TCPModbusChannel(ModbusChannelBasic):
    """
    串口转TCP版的MODBUS通道
    """
    def __init__(self, host, port, **kwargs):
        self.serial = socket.socket()
        self.serial.connect((host, port))

    def read(self, size=1):
        return self.serial.recv(size)

    def write(self, data):
        return self.serial.send(data)

    def close(self):
        pass

    @classmethod
    def read_multiple_register(cls, dev_address, function_code, starting_address, quantity_registers):
        frame = super().read_multiple_register(dev_address, function_code, starting_address, quantity_registers)
        crc = calculate_crc16(b"".join(frame))
        frame.append(struct.pack("<H", crc))
        return frame

    @classmethod
    def write_single_register(cls, dev_address, register_address, register_value):
        frame = super().write_single_register(dev_address, register_address, register_value)
        crc = calculate_crc16(b"".join(frame))
        frame.append(struct.pack("<H", crc))
        return frame


class SerialModbusChannel(ModbusChannelBasic):
    """
    串口版的MODBUS通道
    """
    def __init__(self, **kwargs):
        self.serial = serial.Serial(**kwargs)

    def read(self, size=1):
        return self.serial.read(size)

    def write(self, data):
        return self.serial.write(data)

    def close(self):
        pass

    @classmethod
    def read_multiple_register(cls, dev_address, function_code, starting_address, quantity_registers):
        frame = super().read_multiple_register(dev_address, function_code, starting_address, quantity_registers)
        crc = calculate_crc16(b"".join(frame))
        frame.append(struct.pack("<H", crc))
        return frame

    @classmethod
    def write_single_register(cls, dev_address, register_address, register_value):
        frame = super().write_single_register(dev_address, register_address, register_value)
        crc = calculate_crc16(b"".join(frame))
        frame.append(struct.pack("<H", crc))
        return frame


class ZLGCANCOMModbusChannel(ModbusChannelBasic):
    """
    ZLG CAN-COM100+ CAN版的MODBUS通道
    """
    def open(self):
        pass

    def close(self):
        pass

    def x03_read(self, dev_address, reg_address):
        return modbus.ModbusX03Response()

    def x06_write(self, dev_address, reg_address, reg_bin_value):
        return modbus.ModbusX06Response()


def do_multiple_read_request(channel, device_address, function_code, exception_code_list,
                             starting_address, count_of_registers):
    frame = channel.read_multiple_register(device_address, function_code, starting_address, count_of_registers)
    logging.debug(["TX:", " ".join(["%02X" % x for x in b"".join(frame)])])
    channel.write(b"".join(frame))

    head = channel.read(2)
    if len(head) < 2:
        print("** head len error")
        return

    if head[1] == function_code:
        need = 1 + count_of_registers * 2 + 2
    elif head[1] in exception_code_list:
        need = 1 + 2
    elif head[1] == 0x89:
        print("** status error code: 0x89", head, channel.read(6))
        return
    else:
        print("** status error", head, channel.read(3))
        return

    append_data = channel.read(need)
    if len(append_data) != need:
        print("** data len error")
        return

    data = head + append_data
    logging.debug("".join(("RX:", " ".join(["%02X" % x for x in data]))))

    if head[1] in exception_code_list:
        print("exception response")
        return

    return data


def do_single_write_request(channel, device_address, function_code, exception_code_list,
                            register_address, register_value):
    frame = channel.write_single_register(device_address, register_address, register_value)
    logging.debug("".join(("TX:", " ".join(["%02X" % x for x in b"".join(frame)]))))
    channel.write(b"".join(frame))

    head = channel.read(2)
    if len(head) < 2:
        print("** head len error")
        return

    if head[1] == function_code:
        need = 2 + 2 + 2
    elif head[1] in exception_code_list:
        need = 1 + 2
    elif head[1] == 0x89:
        print("** status error code: 0x89", head, channel.read(6))
        return
    else:
        print("** status error", head, channel.read(3))
        return

    append_data = channel.read(need)
    if len(append_data) != need:
        print("** data len error")
        return

    data = head + append_data
    logging.debug("".join(("RX:", " ".join(["%02X" % x for x in data]))))

    if head[1] in exception_code_list:
        print("exception response")
        return

    return data


if __name__ == '__main__':
    import time
    serial = Serial2TCPModbusChannel()
    exception_code = [0x83]

    while True:
        data = do_multiple_read_request(serial, 0x01, 0x03, exception_code, 0x000A, 10)
        print(data)
        time.sleep(3)

