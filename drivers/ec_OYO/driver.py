# -*- coding: utf-8 -*-
# 这个文件提供了一个设备驱动模板
import profile
import api
import time
import os
import plog
import socket
import json
from . import oyo


class Information:
    # 设备名称
    device_name = '环境箱'
    # 设备类型代码
    dev_type = 'ec'
    # 生产商名称
    vendor = 'OYO'
    # 支持的设备型号
    model = 'CLCD-9700-GF1'
    # 支持的版本
    version = '5版'

    def __str__(self):
        return '<{}/{}/{}/{}>'.format(self.dev_type, self.vendor, self.model, self.vendor)

    # 函数接口, 设备支持的遥控遥调功能
    @staticmethod
    def get_functions_list():
        return oyo.function_list

    # 数据寄存器, 测遥信保持寄存器
    @staticmethod
    def data_register_list():
        return oyo.data_register_list

    # 控制只读寄存器, 遥调遥控下发值
    @staticmethod
    def control_register_list():
        return {}


class Install:
    """驱动安装时调用"""
    def __init__(self):
        pass

    def install(self):
        print("执行{}模拟驱动安装程序".format(Information.device_name))


class Uninstall:
    """驱动卸载时调用"""
    def __init__(self):
        pass

    def uninstall(self):
        print("执行{}模拟驱动卸载程序".format(Information.device_name))


class TCPChannel:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.fds = None

    def open(self):
        if self.fds:
            return self

        self.fds = socket.socket()
        self.fds.connect((self.host, self.port))

        return self

    def close(self):
        if self.fds:
            self.fds.close()

    def read(self, n):
        pass

    def write(self, b):
        pass


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
        self.channel_host = '10.211.55.3'
        self.channel_port = 8234

        self.pubsub = profile.alloc_subscriber()
        self.startup_tsp = time.time()

    def open_channel(self):
        if self.channel:
            self.channel.close()

        return TCPChannel(self.channel_host, self.channel_port).open()

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
        #self.channel = self.open_channel()

        self.pubsub.psubscribe(profile.get_device_control_command_path(Information.dev_type))

        while True:
            # 200毫秒用于等待命令消息
            pack = self.pubsub.get_message(ignore_subscribe_messages=True, timeout=0.2)
            if pack:
                data = json.loads(pack['data'])
                request = api.Request.load_request_from_json(data)
                response = oyo.process_control(self.channel, self.address, request, **request.payload)
            else:
                request = None
                response = None

            self.period_controller.probe_period_delay()
            input_registers = oyo.device_read_all_register(self.channel, self.address)
            if input_registers is None:
                plog.error("返回数据错误, 5秒后重连")
                time.sleep(5)
                self.channel.close()
                self.channel = self.open_channel()
                continue

            if pack and request:
                if not response:
                    api.IncorrectResponse(request, '没有正确应答').do_response()
                else:
                    response.do_response()

            api.device_set_data_registers(Information.dev_type, input_registers)

            time.sleep(0.3)
