# -*- coding: utf-8 -*-
# 这个文件提供了一个设备驱动模板
import profile
import api
import time
import os


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
        return {
            '设置运行模式': {
                "type": 'string',
                "valid_range": ['自动模式', '待机模式'],
                "valid_string": '自动模式/待机模式',
                "comment": "调整设备的运行模式",
                "unit": ""
            },
            '设置冷却液流量': {
                "type": 'float',
                "valid_range": [0, 99.9],
                "valid_string": "0 ~ 99.9",
                "comment": "调整设备冷却液流速",
                "unit": "L/min"
            },
            '设置冷却液温度': {
                "type": 'float',
                "valid_range": [-99.9, 99.9],
                "valid_string": "-99.9 ~ 99.9",
                "comment": "调整设备冷却液温度",
                "unit": "摄氏度"
            },
            '设置加热功率': {
                "type": 'float',
                "valid_range": [0, 101],
                "valid_string": "0 ~ 101",
                "comment": "设置加热功率倍率",
                "unit": "%"
            },
            '设置循环模式': {
                "type": 'string',
                "valid_range": ['内循环', '外循环'],
                "valid_string": "内循环/外循环",
                "comment": "调整设备的循环模式"
            },
            '运行程序号': {
                "type": 'int',
                "valid_range": [0, 255],
                "valid_string": "0~255",
                "comment": "运行程序号",
                "unit": ""
            }
        }

    # 数据寄存器, 测遥信保持寄存器
    @staticmethod
    def data_register_list():
        return {
            '出液温度': {
                "type": 'float',
                "valid_range": [-99.9, 99.9],
                "valid_string": "-99.9 ~ 99.9",
                "comment": "出液温度",
                "unit": "摄氏度"
            },
            '回液温度': {
                "type": 'float',
                "valid_range": [-99.9, 99.9],
                "valid_string": "-99.9 ~ 99.9",
                "comment": "回液温度",
                "unit": "摄氏度"
            },
            '流量': {
                "type": 'float',
                "valid_range": [-99.9, 99.9],
                "valid_string": "-99.9 ~ 99.9",
                "comment": "流量",
                "unit": "L/min"
            },
            '压力': {
                "type": 'float',
                "valid_range": [0, 15.9],
                "valid_string": "0 ~ 15.9",
                "comment": "压力",
                "unit": "bar"
            },
        }

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
        
    def install(self):
        print("执行{}模拟驱动安装程序".format(Information.device_name))


class Uninstall:
    """驱动卸载时调用"""
    def __init__(self):
        pass

    def uninstall(self):
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
        print(profile.platform_root_dir)
        print("{}模拟驱动启动中！".format(Information.device_name))

        while True:
            statement = self.get_driver_statement()
            api.device_set_profile_statement(self.dev_type, statement)
            time.sleep(5)
