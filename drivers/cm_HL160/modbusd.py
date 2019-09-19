# -*- coding: utf8 -*-
import logging
import time
import channel
import settings
import os


if __name__ == '__main__':
    filename = "".join(["modbusd-", str(time.strftime("%Y-%m-%d_%H-%M-%S")), "-", str(os.getpid()), '.log'])
    FORMAT = '[%(levelname)s %(asctime)-15s] %(message)s'
    logging.basicConfig(filename=filename, format=FORMAT, level=logging.DEBUG)

    port = settings.serial_port
    dev_address = settings.modbus_dev_address
    device = __import__("model_" + settings.modbus_model)
    device.initialize_device(dev_address)

    while True:
        try:
            serial_channel = channel.SerialModbusChannel(port=port, timeout=2)
            device.init_all_registers(serial_channel, dev_address)

            while True:
                device.read_all_coils_register(serial_channel, dev_address)
                device.read_all_discrete_input_register(serial_channel, dev_address)
                device.read_all_holding_register(serial_channel, dev_address)
                device.read_all_input_register(serial_channel, dev_address)

                if device.write_all_custom_settings_register(serial_channel, dev_address):
                    device.read_all_holding_register(serial_channel, dev_address)

                time.sleep(0.3)
        except ValueError:
            time.sleep(1)
            device.initialize_device(dev_address)
            continue
