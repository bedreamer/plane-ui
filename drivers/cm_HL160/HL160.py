# -*- coding: utf8 -*-
__version__ = "中汽研版设备的MODBUS通讯程序"


import logging
from . import channels
import struct
import json
import time
import api
import profile


dev_model = "forZQY"

function_list = {
    # '设置运行模式': {
    #     "type": 'string',
    #     "valid_range": ['自动模式', '待机模式'],
    #     "valid_string": '自动模式/待机模式',
    #     "comment": "调整设备的运行模式",
    #     "unit": ""
    # },
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
    },
    '远程定值程序模式选择': {
        "type": 'int',
        "valid_range": [0, 255],
        "valid_string": "0~255",
        "comment": "远程定值程序模式选择",
        "unit": ""
    },
    '远程排汽加液_启动循环泵': {
        "type": 'int',
        "valid_range": [],
        "valid_string": "",
        "comment": "启动循环泵",
        "unit": ""
    },
    '远程排汽加液_停止循环泵': {
        "type": 'int',
        "valid_range": [],
        "valid_string": "",
        "comment": "停止循环泵",
        "unit": ""
    },
    '远程启动': {
        "type": 'int',
        "valid_range": [],
        "valid_string": "",
        "comment": "远程启动",
        "unit": ""
    },
    '远程停止': {
        "type": 'int',
        "valid_range": [],
        "valid_string": "",
        "comment": "远程停止",
        "unit": ""
    },
}

data_register_list = {
    "供液压力显示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "回液压力显示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "供液流量显示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "膨胀罐液位显示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "阀门开度显示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    "供液温度显示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "排气温度显示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "回液温度显示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "冷凝液温度显示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    '加热器超温报警': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '压缩机排气温度高报警': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '压缩机低压保护': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '压缩机高压保护': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    '电源故障相序错误指示': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '补液流量低报警': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    '供液压力传感器故障': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '供液压力超压报警': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    '回液压力传感器故障': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '供液流量超限报警': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '膨胀罐液位传感器故障': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '供液流量传感器故障': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    '膨胀罐液位高报': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '膨胀罐液位低报': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '谷轮涡旋压缩机总报警': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    '供液超温报警': {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    "加热器运行状态": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "压缩机运行指示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "循环泵运行指示": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "电动三通阀开关": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "电动球阀": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "通讯状态检测": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    "远程定值温度设定": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    "远程流量设定": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "远程强制控制加热器": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "远程运行程序号": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "远程启动": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "远程定值程序模式选择": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "远程排汽加液_启动循环泵": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "远程内外循环切换": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "远程停止": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },

    "外部温度K1": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "外部温度K2": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "外部温度K3": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
    "外部温度K4": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "-99.9 ~ 99.9",
        "comment": "出液温度",
        "unit": "摄氏度"
    },
}


def read_all_registers(serial_channel, dev_address):
    exception_code = [0x83]
    register_bytes = channels.do_multiple_read_request(serial_channel, dev_address, 0x03, exception_code, 0x0000, 30)
    if not register_bytes:
        logging.error("读取前50个寄存器失败!")
        return None, None

    input_regs = dict()
    hold_regs = dict()

    def register_number(a):
        """
        裁剪寄存器字节
        :param a: 目标地址
        :return:
            bytes
        """
        begin = 2 * a + 3
        return struct.unpack(">H", register_bytes[begin: begin + 2])[0]

    def float_register(address, dot):
        begin = 2 * address + 3
        value = struct.unpack(">H", register_bytes[begin: begin + 2])[0]
        if value > 0x8000:
            value = (value - 65536) / dot
        else:
            value = value / dot
        return value

    def float_register_x10(address):
        return float_register(address, 10.0)

    def float_register_x100(address):
        return float_register(address, 100.0)

    input_regs["供液压力显示"] = float_register_x100(0x0000)
    input_regs["回液压力显示"] = float_register_x100(0x0001)
    input_regs["供液流量显示"] = float_register_x100(0x0002)
    input_regs["膨胀罐液位显示"] = float_register_x100(0x0003)
    input_regs["阀门开度显示"] = float_register_x100(0x0004)

    input_regs["供液温度显示"] = float_register_x100(0x0005)
    input_regs["排气温度显示"] = float_register_x100(0x0006)
    input_regs["回液温度显示"] = float_register_x100(0x0007)
    input_regs["冷凝液温度显示"] = float_register_x100(0x0008)

    # ----- 设备遥信数据1, 0x0009 -----
    real_data = register_number(0x0009)
    # bit0
    input_regs['加热器超温报警'] = real_data & 0x0001
    input_regs['压缩机排气温度高报警'] = real_data & 0x0002
    input_regs['压缩机低压保护'] = real_data & 0x0004
    input_regs['压缩机高压保护'] = real_data & 0x0008
    # bit4
    input_regs['电源故障相序错误指示'] = real_data & 0x0010
    input_regs['补液流量低报警'] = real_data & 0x0020
    # bit6
    input_regs['供液压力传感器故障'] = real_data & 0x0040
    input_regs['供液压力超压报警'] = real_data & 0x0080
    # bit8
    input_regs['回液压力传感器故障'] = real_data & 0x0100
    input_regs['供液流量超限报警'] = real_data & 0x0200
    input_regs['膨胀罐液位传感器故障'] = real_data & 0x0400
    input_regs['供液流量传感器故障'] = real_data & 0x0800

    # ----- 设备遥信数据2, 0x000A -----
    real_data = register_number(0x000A)
    # bit0
    input_regs['膨胀罐液位高报'] = real_data & 0x0001
    input_regs['膨胀罐液位低报'] = real_data & 0x0002
    input_regs['谷轮涡旋压缩机总报警'] = real_data & 0x0004
    input_regs['供液超温报警'] = real_data & 0x0008

    # ----- 设备工作状态, 0x000B -----
    working_status = register_number(0x000B)
    # bit0
    input_regs["加热器运行状态"] = working_status & 0x0001
    input_regs["压缩机运行指示"] = working_status & 0x0002
    input_regs["循环泵运行指示"] = working_status & 0x0004
    input_regs["电动三通阀开关"] = working_status & 0x0008

    # bit4
    input_regs["电动球阀"] = working_status & 0x0010
    input_regs["通讯状态检测"] = working_status & 0x0020

    # ---- 设备保持寄存器组 ----
    hold_regs["远程定值温度设定"] = float_register_x100(0x000F)

    hold_regs["远程流量设定"] = float_register_x100(0x0010)
    hold_regs["远程强制控制加热器"] = float_register_x100(0x0011)
    hold_regs["远程运行程序号"] = register_number(0x0012)
    hold_regs["远程启动"] = register_number(0x0013)
    hold_regs["远程定值程序模式选择"] = register_number(0x0014)
    hold_regs["远程排汽加液_启动循环泵"] = register_number(0x0015)
    hold_regs["远程内外循环切换"] = register_number(0x0016)
    hold_regs["远程停止"] = register_number(0x0017)

    input_regs["外部温度K1"] = float_register_x10(0x0019)
    input_regs["外部温度K2"] = float_register_x10(0x001A)
    input_regs["外部温度K3"] = float_register_x10(0x001B)
    input_regs["外部温度K4"] = float_register_x10(0x001C)

    return input_regs, hold_regs


def process_control(channel, address, request, function, args):
    exception_code = [0x86]

    def i_设置运行模式(m, *args):
        pass

    def i_设置冷却液流量(l, *args):
        try:
            display_value = float(l) * 10
            modbus_value = int(display_value)
            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0010, modbus_value)
            if not r:
                raise ValueError
            logging.info("远程流量设定：{}".format(modbus_value))
        except KeyError:
            pass

    def i_设置冷却液温度(t, *args):
        try:
            display_value = float(t) * 10
            modbus_value = int(display_value)
            if modbus_value < 0:
                modbus_value += 65536
            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x000F, modbus_value)
            if not r:
                raise ValueError
            logging.info("远程定值温度设定：{}".format(modbus_value))
        except KeyError:
            pass

    def i_设置加热功率(p, *args):
        try:
            modbus_value = int(p) * 100
            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0011, modbus_value)
            if not r:
                raise ValueError
            logging.info("远程强制控制加热器：{}".format(modbus_value))
        except KeyError:
            pass

    def i_设置循环模式(lm, *args):
        try:
            if lm == '内循环':
                modbus_value = 0
            else:
                modbus_value = 1

            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x00016, modbus_value)
            if not r:
                raise ValueError
            logging.info("远程内外循环切换：{}".format(modbus_value))
        except KeyError:
            pass

    def i_运行程序号(n, *args):
        try:
            display_value = int(n)
            modbus_value = int(display_value)
            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0003, modbus_value)
            if not r:
                raise ValueError
            logging.info("远程运行程序号：{}".format(modbus_value))
        except KeyError:
            pass

    def i_远程定值程序模式选择(n, *args):
        try:
            modbus_value = int(n)
            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0014, modbus_value)
            if not r:
                raise ValueError
            logging.info("远程定值程序模式选择：{}".format(modbus_value))
        except KeyError:
            pass

    def i_远程排汽加液_启动循环泵(*args):
        try:
            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0014, 1)
            if not r:
                raise ValueError
        except KeyError:
            pass

    def i_远程排汽加液_停止循环泵(*args):
        try:
            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0014, 0)
            if not r:
                raise ValueError
        except KeyError:
            pass

    def i_远程启动(*args):
        try:
            # 按1送0
            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0013, 1)
            if not r:
                raise ValueError

            time.sleep(1)

            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0013, 0)
            if not r:
                raise ValueError
            logging.info("远程启动")
        except KeyError:
            pass

    def i_远程停止(*args):
        try:
            # 按1送0
            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0017, 1)
            if not r:
                raise ValueError

            time.sleep(1)

            r = channels.do_single_write_request(channel, address, 0x06, exception_code, 0x0017, 0)
            if not r:
                raise ValueError
            logging.info("远程启动")
        except KeyError:
            pass

    def i_not_supported(*args):
        return api.IncorrectResponse(request, "不支持的功能")

    function_route = {
        #'设置运行模式': i_设置运行模式,
        '设置冷却液流量': i_设置冷却液流量,
        '设置冷却液温度': i_设置冷却液温度,
        '设置加热功率': i_设置加热功率,
        '设置循环模式': i_设置循环模式,
        '运行程序号': i_运行程序号,
        '远程定值程序模式选择': i_远程定值程序模式选择,
        '远程排汽加液_启动循环泵': i_远程排汽加液_启动循环泵,
        '远程排汽加液_停止循环泵': i_远程排汽加液_停止循环泵,
        '远程启动': i_远程启动,
        '远程停止': i_远程停止,
    }

    try:
        callback = function_route[function]
    except KeyError:
        callback = i_not_supported

    return callback(*args)


def write_all_custom_settings_register(serial_channel, dev_address):
    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    exception_code = [0x86]
    settings_parameters_path = "%s:%d:设置参数-写入" % (dev_model, dev_address)

    r = profile.alloc_redis()
    result = r.lpop(settings_parameters_path)
    if result is None:
        return

    logging.debug(result)
    try:
        pack = json.loads(result)
    except:
        return


    try:
        # 1 开 0 关
        display_value = pack["远程排汽加液_启动循环泵"]
        modbus_value = int(display_value)
        if modbus_value not in {0, 1}:
            raise KeyError("远程排汽加液控制值必须是0或1")

        r = channels.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0006, modbus_value)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程排汽加液_启动循环泵：{}".format(modbus_value))
    except KeyError:
        pass

