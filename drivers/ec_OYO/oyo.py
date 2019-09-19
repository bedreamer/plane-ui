# -*- coding: utf-8 -*-
# 这个文件提供了一个设备驱动模板
import profile
import api
import time
import os



function_list = {
    # '定值设置': {
    #     "type": 'int',
    #     "valid_range": [0, 99.9],
    #     "valid_string": "0 ~ 99.9",
    #     "comment": "调整设备冷却液流速",
    #     "unit": "L/min"
    # },
    '启动': {
        "type": 'int',
        "valid_range": [],
        "valid_string": "",
        "comment": "启动环境箱",
        "unit": ""
    },
    '停止': {
        "type": 'int',
        "valid_range": [],
        "valid_string": "",
        "comment": "停止环境箱",
        "unit": "%"
    },
    '中止': {
        "type": 'int',
        "valid_range": [],
        "valid_string": "",
        "comment": "中止工作"
    },
}

data_register_list = {
    "测定温度": {
        "type": 'float',
        "valid_range": [-200.0, 250.0],
        "valid_string": "-200.0, 250.0",
        "comment": "测定温度",
        "unit": "°C"
    },
    "测定湿度": {
        "type": 'float',
        "valid_range": [-99.9, 99.9],
        "valid_string": "0.00~100.00",
        "comment": "测定湿度",
        "unit": "%"
    },
    "设定温度": {
        "type": 'float',
        "valid_range": [-200.0, 250.0],
        "valid_string": "-200.0, 250.0",
        "comment": "设定温度",
        "unit": "°C"
    },
    "设定湿度": {
        "type": 'float',
        "valid_range": [0.00, 100.0],
        "valid_string": "0.00~100.00",
        "comment": "出液温度",
        "unit": "%"
    },
    "累计运行_小时": {
        "type": 'float',
        "valid_range": [0, 99999],
        "valid_string": "0 ~ 99999",
        "comment": "累计工作时间的小时数",
        "unit": "小时"
    },
    "累计运行_分钟": {
        "type": 'float',
        "valid_range": [0, 59],
        "valid_string": "0 ~ 59",
        "comment": "累计工作时间的分钟数",
        "unit": "分"
    },
    # "段数": {
    #     "type": 'float',
    #     "valid_range": [-99.9, 99.9],
    #     "valid_string": "-99.9 ~ 99.9",
    #     "comment": "出液温度",
    #     "unit": "摄氏度"
    # },
    # "连接": {
    #     "type": 'float',
    #     "valid_range": [-99.9, 99.9],
    #     "valid_string": "-99.9 ~ 99.9",
    #     "comment": "出液温度",
    #     "unit": "摄氏度"
    # },
    # "程式组": {
    #     "type": 'float',
    #     "valid_range": [-99.9, 99.9],
    #     "valid_string": "-99.9 ~ 99.9",
    #     "comment": "出液温度",
    #     "unit": "摄氏度"
    # },
    "全部循环执行次数": {
        "type": 'int',
        "valid_range": [0, 9999],
        "valid_string": "0 ~ 9999",
        "comment": "全部循环执行次数",
        "unit": "次"
    },
    "全部循环剩余次数": {
        "type": 'int',
        "valid_range": [0, 9999],
        "valid_string": "0 ~ 9999",
        "comment": "全部循环剩余次数",
        "unit": "次"
    },
    "部分循环执行次数": {
        "type": 'int',
        "valid_range": [0, 999],
        "valid_string": "0 ~ 999",
        "comment": "部分循环执行次数",
        "unit": "次"
    },
    "部分循环剩余次数": {
        "type": 'int',
        "valid_range": [0, 999],
        "valid_string": "0 ~ 999",
        "comment": "部分循环剩余次数",
        "unit": "次"
    },
    # "部分循环起始段数": {
    #     "type": 'float',
    #     "valid_range": [-99.9, 99.9],
    #     "valid_string": "-99.9 ~ 99.9",
    #     "comment": "出液温度",
    #     "unit": "摄氏度"
    # },
    # "部分循环终止段数": {
    #     "type": 'float',
    #     "valid_range": [-99.9, 99.9],
    #     "valid_string": "-99.9 ~ 99.9",
    #     "comment": "出液温度",
    #     "unit": "摄氏度"
    # },
    "剩余时间_小时": {
        "type": 'float',
        "valid_range": [0, 9999],
        "valid_string": "0 ～ 999",
        "comment": "剩余小时数",
        "unit": "小时"
    },
    "剩余时间_分钟": {
        "type": 'float',
        "valid_range": [0, 59],
        "valid_string": "0 ~ 59",
        "comment": "剩余分钟数",
        "unit": "分"
    },
    "温度_SSR": {
        "type": 'float',
        "valid_range": [0, 100],
        "valid_string": "0 ~ 100",
        "comment": "温度_SSR",
        "unit": "%"
    },
    "温度_SCR": {
        "type": 'float',
        "valid_range": [0, 100],
        "valid_string": "0 ~ 100",
        "comment": "温度_SCR",
        "unit": "%"
    },
    "湿度_SSR": {
        "type": 'float',
        "valid_range": [0, 100],
        "valid_string": "0 ~ 100",
        "comment": "湿度_SSR",
        "unit": "%"
    },
    "湿度_SCR": {
        "type": 'float',
        "valid_range": [0, 100],
        "valid_string": "0 ~ 100",
        "comment": "湿度_SCR",
        "unit": "%"
    },
    "当前日期": {
        "type": 'string',
        "valid_range": [],
        "valid_string": "YYMMDD",
        "comment": "当前日期",
        "unit": ""
    },
    "当前时间": {
        "type": 'string',
        "valid_range": [],
        "valid_string": "HHMMSS",
        "comment": "当前时间",
        "unit": ""
    },
    "累计运行统计_天": {
        "type": 'float',
        "valid_range": [0, 1999],
        "valid_string": "0 ～ 1999",
        "comment": "累计运行统计天",
        "unit": "天"
    },
    "累计运行统计_小时": {
        "type": 'int',
        "valid_range": [0, 23],
        "valid_string": "0 ~ 23",
        "comment": "累计运行统计小时",
        "unit": "小时"
    },
}


def calc_fcs(xb):
    """
    计算FCS校验码
    """
    if isinstance(xb, str):
        xb = xb.encode()

    o = xb[0]
    for b in xb[1:]:
        o = o ^ b

    return o & 0xFF


def do_request(channel, request_frame, need_bytes, timeout=None):
    print("TX[{}]:".format(len(request_frame)), request_frame)
    echo_ahead = ''.join([request_frame[:5], '0' * (need_bytes - 10)])
    fcs = calc_fcs(echo_ahead)
    echo_frame = ''.join([echo_ahead, '{:02X}'.format(fcs), '\x2A\x0D\x0A'])

    print("RX[{}]:".format(len(echo_frame)), echo_frame)
    return echo_frame


def cut_slice(xb, b, l):
    return xb[b: b + l]


def device_read_all_register(channel, address):
    # 读测定值

    vmap = dict()
    # 命令: 读取类比信息， 
    code = '01'
    # 应答长度
    echo_length = 80
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)
    vmap['测定温度'] = cut_slice(response_bytes, 5, 4)
    vmap['测定湿度'] = cut_slice(response_bytes, 9, 4)
    vmap['设定温度'] = cut_slice(response_bytes, 13, 4)
    vmap['设定湿度'] = cut_slice(response_bytes, 17, 4)
    vmap['累计运行_小时'] = cut_slice(response_bytes, 21, 6)
    vmap['累计运行_分钟'] = cut_slice(response_bytes, 27, 2)
    vmap['段数'] = cut_slice(response_bytes, 29, 4)
    vmap['连接'] = cut_slice(response_bytes, 33, 2)
    vmap['程式组'] = cut_slice(response_bytes, 35, 2)
    vmap['全部循环执行次数'] = cut_slice(response_bytes, 37, 4)
    vmap['全部循环剩余次数'] = cut_slice(response_bytes, 41, 4)
    vmap['部分循环执行次数'] = cut_slice(response_bytes, 45, 4)
    vmap['部分循环剩余次数'] = cut_slice(response_bytes, 49, 4)
    vmap['部分循环起始段数'] = cut_slice(response_bytes, 53, 4)
    vmap['部分循环终止段数'] = cut_slice(response_bytes, 57, 4)
    vmap['剩余时间_小时'] = cut_slice(response_bytes, 61, 4)
    vmap['剩余时间_分钟'] = cut_slice(response_bytes, 65, 2)
    vmap['温度_SSR'] = cut_slice(response_bytes, 67, 2)
    vmap['温度_SCR'] = cut_slice(response_bytes, 69, 2)
    vmap['湿度_SSR'] = cut_slice(response_bytes, 71, 2)
    vmap['湿度_SCR'] = cut_slice(response_bytes, 73, 2)

    # 命令: 读取时期时间信息， 
    code = '03'
    # 应答长度
    echo_length = 28
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)
    vmap['当前日期'] = cut_slice(response_bytes, 5, 6)
    vmap['当前时间'] = cut_slice(response_bytes, 11, 6)
    vmap['累计运行统计_天'] = cut_slice(response_bytes, 17, 4)
    vmap['累计运行统计_小时'] = cut_slice(response_bytes, 21, 2)

    # 命令: 读取设备状态信息， 
    code = '51'
    # 应答长度
    echo_length = 22
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)
    block_1 = cut_slice(response_bytes, 5, 4)
    block_2 = cut_slice(response_bytes, 9, 4)
    block_3 = cut_slice(response_bytes, 13, 4)
    vmap['block_1'] = block_1
    vmap['block_2'] = block_2
    vmap['block_3'] = block_3

    # 命令: 读取剩余步骤， 
    code = '80'
    # 应答长度
    echo_length = 14
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)
    vmap['剩余段数'] = cut_slice(response_bytes, 5, 4)

    return vmap
    

def device_settings(channel, address, request, wendu, shidu, k_wendu, k_shidu, hour, mini, tm, standby, sig):
    # 命令: 读取设备状态信息， 
    code = '15'
    # 应答长度
    echo_length = 22
    
    hex_wendu = '0000'
    hex_shidu = '0000'
    hex_k_wendu = '0000'
    hex_k_shidu = '0000'
    hex_hour = '0000'
    hex_mini = '00'
    hex_tm = '0'
    hex_standby = '0'
    hex_sig = '000'
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code,
        hex_wendu,
        hex_shidu,
        hex_k_wendu,
        hex_k_shidu,
        hex_hour,
        hex_mini,
        hex_tm,
        hex_standby,
        hex_sig
    ])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)


def device_control_run(channel, address, request):
    # 命令: 操作设定， 启动
    code = '53'
    # 控制码
    control_code = '01'
    # 应答长度
    echo_length = 13
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code, control_code, '1'])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)


def device_control_stop(channel, address, request):
    # 命令: 操作设定， 停止
    code = '53'
    # 控制码
    control_code = '02'
    # 应答长度
    echo_length = 13
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code, control_code, '1'])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)


def device_control_hold(channel, address, request, hold):
    # 命令: 操作设定， 保持
    code = '53'
    # 控制码
    control_code = '03'
    # 应答长度
    echo_length = 13
    
    if hold == 0:
        hold_code = '0'
    else:
        hold_code = '1'
    
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code, control_code, hold_code])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)


def device_control_advance(channel, address, request):
    # 命令: 操作设定， 跳过
    code = '53'
    # 控制码
    control_code = '04'
    # 应答长度
    echo_length = 13
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code, control_code, '1'])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)


def device_control_pause(channel, address, request):
    # 命令: 操作设定， 中止
    code = '53'
    # 控制码
    control_code = '05'
    # 应答长度
    echo_length = 13
    request_ahead = ''.join(['@', '{:02X}'.format(address&0xff), code, control_code, '1'])
    fcs = calc_fcs(request_ahead)
    request_frame = ''.join([request_ahead, '{:02X}'.format(fcs), '\x2A\x0D'])
    response_bytes = do_request(channel, request_frame, echo_length)


def process_control(channel, address, request, function, args):

    def i_not_supported(*args):
        return api.IncorrectResponse(request, "不支持的功能")

    function_route = {
        '启动': device_control_run,
        '停止': device_control_stop,
        # '设置加热功率': device_control_hold,
        # '设置循环模式': device_control_advance,
        '中止': device_control_pause,
    }

    try:
        callback = function_route[function]
    except KeyError:
        callback = i_not_supported

    return callback(channel, address, request, *args)

