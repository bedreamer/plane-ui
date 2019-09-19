# -*- coding: utf-8 -*-
# 这个文件提供了一个设备驱动模板
import profile
import api
import time
import os
import sys
import random
import plog
import json
from . import HL160 as drv
from . import channels


class Information:
    # 设备名称
    device_name = '水冷机'
    # 设备类型代码
    dev_type = 'cm'
    # 生产商名称
    vendor = 'newline'
    # 支持的设备型号
    model = 'HL-160'
    # 支持的版本
    version = 'V1.0'

    def __str__(self):
        return '<{}/{}/{}/{}>'.format(self.dev_type, self.vendor, self.model, self.vendor)

    # 函数接口, 设备支持的遥控遥调功能
    @staticmethod
    def get_functions_list():
        return drv.function_list

    # 数据寄存器, 测遥信保持寄存器
    @staticmethod
    def data_register_list():
        return drv.data_register_list

    # 控制只读寄存器, 遥调遥控下发值
    @staticmethod
    def control_register_list():
        return {
            '设置运行模式': {},
            '设置流量': {},
            '设置温度': {},
            '设置加热功率': {},
            '设置': {},
            '运行程序号': {}
        }


class Install:
    """驱动安装时调用"""

    def __init__(self):
        pass

    @staticmethod
    def install():
        print("执行{}模拟驱动安装程序".format(Information.device_name))


class Uninstall:
    """驱动卸载时调用"""

    def __init__(self):
        pass

    @staticmethod
    def uninstall():
        print("执行{}模拟驱动卸载程序".format(Information.device_name))


class Driver:
    """
    这个是驱动样板，驱动主题程序就按这个写
    """

    def __init__(self, model, conf, *args, **kwargs):
        self.model = model
        self.dev_type = self.model.type.code
        self.conf = conf

        self.startup_tsp = time.time()

        self.period_controller = api.PeriodController(period_in_ms=500)

        self.address = 1
        self.channel = None
        self.channel_host = '10.211.55.3'
        self.channel_port = 8234

        self.pubsub = profile.alloc_subscriber()

    def open_channel(self):
        """打开通道"""
        return channels.Serial2TCPModbusChannel(host=self.channel_host, port=self.channel_port)

    def get_driver_statement(self):
        now = time.time()

        ca = time.localtime(self.startup_tsp)
        startup_datetime = time.strftime(profile.DT_FORMAT, ca)

        return {
            'pid': os.getpid(),
            '工作目录': os.getcwd(),
            '启动时间': startup_datetime,
            '运行时间': now - self.startup_tsp,
            'id': self.model.id,
            'device_name': Information.device_name,
            'vendor': self.model.vendor,
            'model': self.model.model,
            'version': self.model.version,
            'dev_type': Information.dev_type,
            'functions': Information.get_functions_list(),
            'registers': Information.data_register_list(),
            'control_registers': Information.control_register_list(),
            '循环周期': self.period_controller.get_period(),
            '动态周期': self.period_controller.get_real_period(),
        }

    def get_all_data_registers(self):
        return {key: random.randrange(*[int(v) for v in value['valid_range']]) for key, value in Information.data_register_list().items()}

    def process_control_command(self):
        """处理设备的控制命令"""
        status, length, reason = api.device_get_control_command_length(self.dev_type)
        if status != api.OK:
            print(reason)
            return

        if not length:
            return

        load = time.time()
        # 执行时间限制在500毫秒
        while length > 0 and time.time() - load < 0.5:
            status, request, reason = api.device_get_control_command(self.dev_type)
            if status != api.OK:
                break

            if request is None:
                break

            if request.is_expire() is True:
                plog.warn("接收到过期的命令：", command=str(request))
                break

            request.dump()
            response = api.IncorrectResponse(request, reason='还未实现')
            response.do_response()
            response.dump()

    def run_until_exit(self, *args, **kwargs):
        plog.info("{}模拟驱动已启动，pid: {}, 工作目录: {}".format(Information.device_name, os.getpid(), os.getcwd()))
        self.channel = self.open_channel()

        self.pubsub.psubscribe(profile.get_device_control_command_path(Information.dev_type))

        while True:
            # 200毫秒用于等待命令消息
            pack = self.pubsub.get_message(ignore_subscribe_messages=True, timeout=0.2)
            if pack:
                data = json.loads(pack['data'])
                request = api.Request.load_request_from_json(data)
                response = drv.process_control(self.channel, self.address, request, **request.payload)
            else:
                request = None
                response = None

            self.period_controller.probe_period_delay()
            input_registers, hold_registers = drv.read_all_registers(self.channel, self.address)
            if None in (input_registers, hold_registers):
                plog.error("返回数据错误, 5秒后重连")
                time.sleep(5)
                self.channel = self.open_channel()
                continue

            if pack and request:
                if not response:
                    api.IncorrectResponse(request, '没有正确应答').do_response()
                else:
                    response.do_response()

            api.device_set_data_registers(Information.dev_type, input_registers)
            api.device_set_hold_registers(Information.dev_type, hold_registers)

            time.sleep(0.3)
