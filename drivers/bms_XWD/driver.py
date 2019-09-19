# -*- coding: utf-8 -*-
# 这个文件提供了一个设备驱动模板
import profile
import api
import time
import os
import sys
import random
import json
import socket
import plog
import device
import cantools
from . import xwd


class Information:
    # 设备名称
    device_name = 'BMS'
    # 设备类型代码
    dev_type = 'bms'
    # 生产商名称
    vendor = '欣旺达'
    # 支持的设备型号
    model = 'B-98'
    # 支持的版本
    version = 'V1.0'

    def __str__(self):
        return '<{}/{}/{}/{}>'.format(self.dev_type, self.vendor, self.model, self.vendor)

    # 函数接口, 设备支持的遥控遥调功能
    @staticmethod
    def get_functions_list():
        return {}

    # 数据寄存器, 测遥信保持寄存器
    @staticmethod
    def data_register_list():
        dbc_file_path = '/'.join([os.path.dirname(os.path.abspath(__file__)), 'default.dbc'])
        db = cantools.database.load_file(dbc_file_path)
        signals_map = dict()
        for message in db.messages:
            for signal in message.signals:
                signals_map[signal.name] = {
                    "type": 'float',
                    "valid_range": [signal.minimum, signal.maximum],
                    "valid_string": '{} ~ {}'.format(signal.minimum, signal.maximum),
                    "comment": signal.comment,
                    "unit": signal.unit
                }
        return signals_map

    # 控制只读寄存器, 遥调遥控下发值
    @staticmethod
    def control_register_list():
        return {}


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
        self.period_controller = api.PeriodController(period_in_ms=500)

        self.address = 1
        self.channel = None
        self.channel_host = '127.0.0.1'
        self.channel_port = 8234

        self.startup_tsp = time.time()

    def open_channel(self):
        if self.channel:
            self.channel.close()

        dbc_file_path = '/'.join([os.path.dirname(os.path.abspath(__file__)), 'default.dbc'])
        return device.USRCANET2TCPClientChannel(self.channel_host, self.channel_port, dbc_file_path).open()

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
        }

    def run_until_exit(self, *args, **kwargs):
        plog.info("{}模拟驱动已启动，pid: {}, 工作目录: {}".format(Information.device_name, os.getpid(), os.getcwd()))
        self.channel = self.open_channel()

        # 初始化设备初始值
        api.device_set_data_registers(Information.dev_type, self.channel.signals_map)
        while True:
            api.device_set_profile_statement(Information.dev_type,self.get_driver_statement())

            self.period_controller.probe_period_delay()
            xwd.device_read_all_register(self.channel)
            api.device_set_data_registers(Information.dev_type, self.channel.signals_map)
            time.sleep(0.3)
