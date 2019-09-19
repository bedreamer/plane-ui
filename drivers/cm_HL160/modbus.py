# -*- coding: utf8 -*-
import logging
import time
import struct


class ModbusBasicException(Exception):
    source = 'Modbus'


class ModbusNotOpen(ModbusBasicException):
    reason = "MODBUS通道未打开"


class ModbusClosed(ModbusBasicException):
    reason = "MODBUS已关闭"


###################################################################


class ModbusRegister(object):
    """
    MODBUS寄存器对象
    """
    def __init__(self, device, register_name, display_name, unit_text, address, supported_function_list,
                 initialize_value, k, b):
        """
        MODBUS寄存器
        :param device: 设备对象
        :param register_name: 寄存器名，字符名
        :param display_name: 显示名，中文
        :param unit_text: 单位
        :param address: 地址
        :param supported_function: 支持的函数功能码列表, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06
        :param initialize_value: 初始值， 只在rw_mode=w时下发这个值
        :param k: 寄存器值与实际值斜率值
        :param b: 寄存器值与实际值偏移量

        Note:
            1. rw_mode 在集合 {rw, rw}时，初始化完成后主动读取寄存器一次
            2. rw_mode 自集合 {w}时，且initialize_value有效时，初始化完成后主动写入寄存器一次，值为initialize_value
            3. 实际值 = 寄存器值 * k + b <==> real_value = register_value * k + b
                eg: 33.4 = 334 * 0.1 + 0
        """
        self.device = device
        self.register_name = register_name
        self.display_name = display_name

        logging.debug("初始化设备%d寄存器：%s", device.get_address(), display_name)
        self.unit_text = unit_text
        self.address = address
        self.supported_function_list = supported_function_list
        self.initialize_value = initialize_value
        self.k = k
        self.b = b

        self._register_value = None

    def get_address(self):
        return self.address

    def set_value(self, real_value):
        """
        设置寄存器值
        :param real_value: 实际值
        :return: 实际值
                寄存器值 = int(实际值 - b) / k
        """
        new_value, old_value = int((real_value - self.b) / self.k), self._register_value
        self._register_value = new_value

        logging.debug("Write [%s:%04X] 从 %s 到 %s", self.display_name, self.address, str(old_value), str(new_value))
        return self.get_value()

    def get_value(self):
        """
        获取实际值
        :return: 实际值
                实际值 = 寄存器值 * k + b
        """
        return self._register_value * self.k + self.b

    def get_register_value(self):
        """
        获取寄存器值
        :return: 寄存器值
        """
        return self._register_value

    def set_register_value(self, register_value):
        self._register_value = register_value

    def initialize(self):
        """
        初始化寄存器
        :return: 1: [<ModbusX03Request object>, ...] 表明需要发起一次或多次读寄存器请求
                 2: [<ModbusX06Request>, ...], 表明需要发起一次或多次写寄存器请求
                 3: None
        """
        if ReadHoldingRegisterRequest.function_code in self.supported_function_list:
            return [ReadHoldingRegisterRequest(self.device, self.address, 1)]
        elif ReadInputRegistersRequest.function_code in self.supported_function_list:
            return [ReadInputRegistersRequest(self.device, self.address, 1)]

        if isinstance(self.initialize_value, int) or isinstance(self.initialize_value, float):
            if WriteSingleCoilRequest.function_code in self.supported_function_list:
                return [WriteSingleCoilRequest(self.device, self.address, self.initialize_value)]
            elif WriteSingleRegisterRequest.function_code in self.supported_function_list:
                return [WriteSingleRegisterRequest(self.device, self.address, self.initialize_value)]

        return None


###################################################################


class ModbusBasicRequest(object):
    """
    MODBUS请求基本类
    """
    def __init__(self, device):
        self.device = device


class ModbusReadRequest(ModbusBasicRequest):
    def __init__(self, device):
        super().__init__(device)

    def do_request(self, channel):
        raise NotImplementedError

    def do_multiple_read_request(self, channel, function_code, exception_code_list, starting_address,
                                 count_of_registers):
        device_address = self.device.get_address()

        frame = channel.read_multiple_register(device_address, function_code, starting_address, count_of_registers)
        print("TX:", " ".join(["%02X" % x for x in b"".join(frame)]))
        channel.write(b"".join(frame))

        head = channel.read(2)
        if len(head) == 2:
            pass
        else:
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
        print("RX:", " ".join(["%02X" % x for x in data]))

        if head[1] in exception_code_list:
            print("exception response")
            return

        body = data[3: len(data)-2]
        for i in range(count_of_registers):
            data = body[i * 2: i * 2 + 2]

            register = self.device.search_register(starting_address + i)
            if register is None:
                continue

            value = struct.unpack(">H", data)[0]
            register.set_register_value(value)

            print("%04X" % register.address, "==>", register.get_value())


class ReadHoldingRegisterRequest(ModbusReadRequest):
    function_code = 0x03
    exception_code_list = [0x83]

    def __init__(self, device, starting_address, quantity_of_registers):
        super().__init__(device)
        self.starting_address = starting_address
        self.quantity_of_registers = quantity_of_registers

        logging.info("0x03 {}, {}".format(starting_address, quantity_of_registers))

    def do_request(self, channel):
        return self.do_multiple_read_request(channel, self.function_code, self.exception_code_list,
                                             self.starting_address, self.quantity_of_registers)


class ReadInputRegistersRequest(ModbusReadRequest):
    function_code = 0x04
    exception_code_list = [0x84]

    def __init__(self, device, starting_address, quantity_of_input_registers):
        super().__init__(device)
        self.starting_address = starting_address
        self.quantity_of_registers = quantity_of_input_registers

        logging.info("0x04 {}, {}".format(starting_address, quantity_of_input_registers))

    def do_request(self, channel):
        return self.do_multiple_read_request(channel, self.function_code, self.exception_code_list,
                                             self.starting_address, self.quantity_of_registers)


class WriteSingleCoilRequest(ModbusBasicRequest):
    function_code = 0x05
    exception_code = 0x85

    def __init__(self, device, output_address, output_value):
        super().__init__(device)
        self.output_address = output_address
        self.output_value = output_value

        logging.info("0x05 {}, {}".format(output_address, output_value))

    def do_request(self, channel):
        pass


class WriteSingleRegisterRequest(ModbusBasicRequest):
    function_code = 0x06
    exception_code = 0x86

    def __init__(self, device, register_address, register_value):
        super().__init__(device)
        self.register_address = register_address
        self.register_value = register_value

    def do_request(self, channel):
        pass


class ModbusResponseBasic(object):
    """
    MODBUS应答基本类
    """
    pass


class ModbusX03Response(ModbusResponseBasic):
    """
    MODBUS读单个寄存器应答对象
    """
    pass


class ModbusX06Response(ModbusResponseBasic):
    """
    MODBUS写单个寄存器请求对象
    """
    pass


###################################################################


class ModbusDevice(object):
    def __init__(self, dev_address):
        self.dev_address = dev_address
        logging.debug("创建MODBUS设备, 地址: %d", self.dev_address)

        self.registers_map = dict()
        self.last_communication = 0

        self.holding_register_list = list()
        self.input_register_list = list()

        # 保持寄存器的请求列表
        self.read_holding_register_request_list = list()
        # 输入寄存器的请求列表
        self.read_input_register_request_list = list()

    def get_address(self):
        return self.dev_address

    def search_register(self, address):
        """
        根据给定的寄存器地址搜索寄存器对象
        :param address: 寄存器地址
        :return: <ModbusRegister object>
        """
        try:
            return self.registers_map[address]
        except KeyError:
            return None

    def make_continue_request(self, sorted_register_list, request_class):
        # 初始化保持寄存器的请求列表
        continue_address = list()
        request_list = list()
        for address in sorted_register_list:
            if len(continue_address) == 0:
                continue_address.append(address)
            elif address == continue_address[-1] + 1:
                continue_address.append(address)
            else:
                starting_address, quantity_of_registers = continue_address[0], len(continue_address)
                request = request_class(self, starting_address, quantity_of_registers)
                request_list.append(request)

                continue_address = [address]

        if len(continue_address):
            starting_address, quantity_of_registers = continue_address[0], len(continue_address)
            request = request_class(self, starting_address, quantity_of_registers)
            request_list.append(request)

        return request_list

    def initialize(self, registers_map):
        """
        初始化MODBUS寄存器映射表
        :param registers_map: 寄存器表
        :return:
        """
        initialize_request_list = list()

        for register_profile in registers_map:
            register = ModbusRegister(self, **register_profile)

            self.registers_map[register.address] = register

            # 保持寄存器的地址列表
            if ReadHoldingRegisterRequest.function_code in register.supported_function_list:
                self.holding_register_list.append(register.address)

            # 输入寄存器的地址列表
            if ReadInputRegistersRequest.function_code in register.supported_function_list:
                self.input_register_list.append(register.address)

            request_list = register.initialize()
            if isinstance(request_list, list):
                initialize_request_list.extend(request_list)

        # 按照寄存器的地址顺序从小到大一次排序
        sorted(self.holding_register_list)
        sorted(self.input_register_list)

        # 初始化保持寄存器的请求列表
        self.read_holding_register_request_list = self.make_continue_request(self.holding_register_list,
                                                                             ReadHoldingRegisterRequest)

        # 初始化输入寄存器的请求列表
        self.read_input_register_request_list = self.make_continue_request(self.input_register_list,
                                                                           ReadInputRegistersRequest)

        return initialize_request_list

    def read_all_holding_register(self, channel):
        request_list = self.read_holding_register_request_list[::]

        for request in request_list:
            request.do_request(channel)

        del request_list

    def read_all_input_register(self, channel):
        request_list = self.read_input_register_request_list[::]

        for request in request_list:
            request.do_request(channel)

        del request_list

    def run_step_forward(self, now, channel):
        if now - self.last_communication < 1:
            return

        self.last_communication = now

        self.read_all_holding_register(channel)
        self.read_all_input_register(channel)

    def on_response(self, request, response):
        logging.info(str(request) + str(response))
        self.last_communication = time.time()


class ModbusDeviceManager(object):
    """
    MODBUS设备管理器
    """

    def __init__(self, channel, devices_address_list, registers_map):
        self._channel = channel
        self._devices_address_list = set(devices_address_list)
        self._registers_map = registers_map

        self._devices = list()

    def initialize(self):
        if len(self._devices_address_list) == 0:
            logging.error("需要提供设备地址列表, eg: [1,2,3]")
            return False

        if max(self._devices_address_list) > 255:
            logging.error("设备最大地址不能超过255")
            return False

        if min(self._devices_address_list) < 0:
            logging.error("设备最小地址不能低于0")
            return False

        if len(self._registers_map) == 0:
            logging.error("需要提供寄存器映射表")
            return False

        # 初始化设备
        initialize_request_list = list()
        for dev_address in self._devices_address_list:
            device = ModbusDevice(dev_address=dev_address)

            device_initialize_request_list = device.initialize(self._registers_map)
            initialize_request_list.extend(device_initialize_request_list)

            self._devices.append(device)

        for request in initialize_request_list:
            request.do_request(self._channel)

        return True

    def run_step_forward(self, now=None):
        now = time.time() if now is None else now

        for device in self._devices:
            device.run_step_forward(now, self._channel)
