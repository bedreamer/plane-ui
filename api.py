# -*- coding: utf-8 -*-
# author: lijie
# 提供给UI，用于和后段进行交互
#
# api 函数包含 设备驱动（device），流程控制（flow), 项目（project）几大类
# 函数返回结构为一个三元组：(状态，结果，原因), 其中状态属于集合{OK, ERROR},
# 原因为字符串，结果根据API功能而不同。
# v1.0 2019-08-10
# 开始构建API接口
#
# v1.1 2019-08-15
# 改变API返回状态
# 前一版本中:
#  若redis返回None，认为这个API是失败的，会返回E_REDIS_SERVER_EMPTY_RETURN错误，这种错误会和路径检查机制
#  产生冲突，路径检查机制是：
#  进程会周期性的检查某个路径上的数据改变状态，此时若没有数据的话会导致返回该错误，从而引起连续的故障堆栈保存，
#  为了避免这种问题，现在将返回None认为API调用成功。
#  也就是说：只要redis返回数据，就认为API调用成功，至于数据有效性判断需要在具体的业务代码中去判定
#
#
import json
import socket
import redis
import uuid
import time
import subprocess
import plog
import codecs
import inspect
import shutil
import plane
from storage.models import *
import profile
import flowex


E_CONNECT_REDIS_SERVER_ERROR = '链接redis服务器{}:{}失败'.format(profile.redis_host, profile.redis_port)
E_CONNECT_REDIS_SERVER_TIMEOUT = '链接redis服务器{}:{}超时'.format(profile.redis_host, profile.redis_port)
E_REDIS_SERVER_EMPTY_RETURN = 'redis服务器返回空数据。考虑键值是否存在？'
E_UNSUPPORTED_DATA_TYPE = 'redis服务器返回数据类型不受支持，只支持(str, bytes, bool)'
E_JSON_DECODE_ERROR = 'JSON解码错误'
E_KEY_ERROR = '键值错误'


# API调用成功标识
OK = 'ok'
# API调用失败标识
ERROR = 'error'


def save_error_information(stack_dump_list):
    """
    将错误堆栈保存到文件中
    :return：
        uuid, filename
    """
    error_id = str(uuid.uuid1())
    tsp_datetime = time.strftime(profile.DT_FORMAT)
    error_log_path = profile.error_log_entry_file
    with codecs.open(error_log_path, mode='a+', encoding=profile.encoding) as file:
        file.write("错误ID: {}\n".format(error_id))
        file.write("时间戳: {}\n".format(tsp_datetime))
        file.write("============================\n")
        json.dump(stack_dump_list, file, ensure_ascii=False, indent=2)
        file.write('\n\n\n\n')

    stat = os.stat(error_log_path)
    if stat.st_size < profile.LOG_FILE_MAX_SIZE:
        return error_id, error_log_path
    else:
        # 单个文件超过指定大小后将其重新命名，添加后缀
        timestamp = time.strftime(profile.DT_TIMESTAMP)
        target_file = ''.join([error_log_path, timestamp, '.log'])
        shutil.move(error_log_path, target_file)
        return error_id, target_file


class ErrorReason(dict):
    """故障原因摘要信息"""
    def __init__(self, subscript, **kwargs):
        self.subscript = subscript
        self.kwargs = kwargs
        super().__init__(self, subscript=subscript, **kwargs)

    def __str__(self):
        return '\n'.join([
            self.subscript,
            json.dumps(self.kwargs, ensure_ascii=False, indent=2)
        ])


def is_connection_error(reason):
    """根据原因判断是否时网络断开错误"""
    return True if reason.subscript in {E_CONNECT_REDIS_SERVER_ERROR, E_CONNECT_REDIS_SERVER_TIMEOUT} else False


def return_ok_payload(payload=None, reason=None):
    """返回正常应答"""
    return OK, payload, ErrorReason('no error' if reason is None else reason)


def return_warning_payload(reason, payload=None, **kwargs):
    """返回错误应答，但不记录日志"""
    if isinstance(reason, ErrorReason):
        return ERROR, payload, reason
    else:
        return ERROR, payload, ErrorReason(reason, **kwargs)


def return_error_payload(reason, payload=None, **kwargs):
    """返回错误应答, 并记录日志"""
    root_frame = inspect.currentframe()
    try:
        frame_list = inspect.getouterframes(root_frame)
        call_stack = list()
        for idx, caller in enumerate(frame_list[1:]):
            stack = dict()
            stack['deep'] = idx
            stack['filename'] = caller.filename
            stack['function'] = caller.function
            stack['lineno'] = caller.lineno
            stack['local'] = {key: str(value) for key, value in caller.frame.f_locals.items()}
            call_stack.append(stack)

        kwargs['错误ID'], kwargs['错误记录文件'] = save_error_information(call_stack)
        kwargs['错误来源堆栈'] = call_stack[0]
    finally:
        # TODO: 如果出现内存膨胀的问题，首先从这里开始查起，问题参考链接如下：
        # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
        del root_frame

    plog.warn("API/函数调用失败", reason=reason, **kwargs)
    return return_warning_payload(reason, payload, **kwargs)


def _return_parse_data_from_redis(result):
    """解析来自redis的数据"""
    try:
        if isinstance(result, bytes):
            payload = json.loads(result.decode())
        elif isinstance(result, str):
            payload = json.loads(result)
        elif isinstance(result, bool):
            payload = result
        elif isinstance(result, int):
            payload = result
        elif result is None:
            payload = None
        else:
            return return_error_payload(E_UNSUPPORTED_DATA_TYPE, msg=str(result.decode()))
    except json.JSONDecodeError:
        return return_error_payload(E_JSON_DECODE_ERROR, msg=str(result.decode()))

    return return_ok_payload(payload)


"""      redis API封装   """


def lindex(path, index):
    """获取通用的redis列表数据"""
    try:
        rds = profile.public_redis
        result = rds.lindex(path, index)
    except socket.timeout:
        return return_error_payload(E_CONNECT_REDIS_SERVER_TIMEOUT)
    except socket.gaierror:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except socket.error:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except redis.exceptions.ConnectionError:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)

    return _return_parse_data_from_redis(result)


def llen(path):
    """获取通用的redis列表长度"""
    try:
        rds = profile.public_redis
        result = rds.llen(path)
    except socket.timeout:
        return return_error_payload(E_CONNECT_REDIS_SERVER_TIMEOUT)
    except socket.gaierror:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except socket.error:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except redis.exceptions.ConnectionError:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)

    return _return_parse_data_from_redis(result)


def lpop(path):
    """获取通用的redis列表的第一个数据"""
    try:
        rds = profile.public_redis
        result = rds.lpop(path)
    except socket.timeout:
        return return_error_payload(E_CONNECT_REDIS_SERVER_TIMEOUT)
    except socket.gaierror:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except socket.error:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except redis.exceptions.ConnectionError:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)

    return _return_parse_data_from_redis(result)


def rpush(path, payload):
    """设置通用的redis列表数据"""
    try:
        rds = profile.public_redis
        if isinstance(payload, str) or isinstance(payload, bytes) or isinstance(payload, bool):
            result = rds.rpush(path, payload)
        else:
            result = rds.rpush(path, json.dumps(payload, ensure_ascii=False, default=lambda o: o.__dict__))
    except socket.timeout:
        return return_error_payload(E_CONNECT_REDIS_SERVER_TIMEOUT)
    except socket.gaierror:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except socket.error:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except redis.exceptions.ConnectionError:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)

    return _return_parse_data_from_redis(result)


def get(path):
    """获取通用的redis字符串数据"""
    try:
        rds = profile.public_redis
        result = rds.get(path)
    except socket.timeout:
        return return_error_payload(E_CONNECT_REDIS_SERVER_TIMEOUT)
    except socket.gaierror:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except socket.error:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except redis.exceptions.ConnectionError:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)

    return _return_parse_data_from_redis(result)


def rset(path, payload, ex=None):
    """设置通用的redis字符串数据"""
    try:
        rds = profile.public_redis
        if isinstance(payload, str) or isinstance(payload, bytes) or isinstance(payload, bool):
            result = rds.set(path, payload, ex=ex)
        else:
            result = rds.set(path, json.dumps(payload, ensure_ascii=False), ex=ex)
    except socket.timeout:
        return return_error_payload(E_CONNECT_REDIS_SERVER_TIMEOUT)
    except socket.gaierror:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except socket.error:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except redis.exceptions.ConnectionError:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)

    return _return_parse_data_from_redis(result)


def rpublish(path, payload):
    """发布消息"""
    try:
        rds = profile.public_redis
        if isinstance(payload, str) or isinstance(payload, bytes) or isinstance(payload, bool):
            result = rds.publish(path, payload)
        else:
            result = rds.publish(path, json.dumps(payload, ensure_ascii=False))
    except socket.timeout:
        return return_error_payload(E_CONNECT_REDIS_SERVER_TIMEOUT)
    except socket.gaierror:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except socket.error:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)
    except redis.exceptions.ConnectionError:
        return return_error_payload(E_CONNECT_REDIS_SERVER_ERROR)

    return _return_parse_data_from_redis(result)


"""      redis 通讯协议   """


class Response:
    """应答"""
    def __init__(self, request, payload, status=None, reason=None):
        self.request = request

        self.payload = payload
        self.status = OK if status is None else status
        self.reason = None if reason is None else reason

    def do_response(self):
        pack = json.dumps({
            'rid': self.request.rid,
            'status': self.status,
            'reason': str(self.reason),
            'payload': self.payload,
        }, ensure_ascii=False)
        path = self.request.echo_path

        return rset(path, pack, ex=self.request.timeout)

    def pairs(self):
        return self.status, self.payload, self.reason

    @staticmethod
    def load_response_from_json(request, j):
        """将json对象加载成response对象"""
        status = j['status']
        reason = j['reason']
        payload = j['payload']

        if status.lower() == OK:
            return CorrectResponse(request, payload)
        else:
            return IncorrectResponse(request, reason, payload)

    def dump(self):
        print("Response")
        print('=' * 20)
        print("rid:", self.request.rid)
        print("status:", self.status)
        print("reason:", self.reason)
        print("payload:", self.payload)
        print('')


class CorrectResponse(Response):
    """正常应答"""
    def __init__(self, request, payload=None):
        super().__init__(request, payload, status=OK, reason=None)

    def __str__(self):
        return '<CorrectResponse for {}>'.format(self.request.rid)


class IncorrectResponse(Response):
    """错误应答"""
    def __init__(self, request, reason=None, payload=None):
        super().__init__(request, payload, status=ERROR, reason=reason)

    def __str__(self):
        return '<IncorrectResponse for {}>'.format(self.request.rid)


class Request:
    def __init__(self, cmd, target_path, payload=None, echo_path=None, timeout=None, expire=None, rid=None, **kwargs):
        self.cmd = cmd

        if rid is None:
            rid = str(uuid.uuid4())
        self.rid = rid

        self.target_path = target_path
        self.echo_path = ''.join([target_path, '-', rid]) if echo_path is None else echo_path

        if timeout is None:
            timeout = 3
        self.timeout = timeout

        expire_tsp = time.time() + timeout
        expire_array = time.localtime(expire_tsp)
        expire = time.strftime(profile.DT_FORMAT, expire_array)
        self.expire = time.time() + timeout if expire is None else expire

        self.payload = dict() if not payload else payload
        self.kwargs = kwargs

        self._sent_tsp = None
        self._sent_fail_reason = None

    def is_expire(self):
        t = time.strptime(self.expire, profile.DT_FORMAT)
        expire = time.mktime(t)
        if expire < time.time():
            return True
        else:
            return False

    def __str__(self):
        return str(self.get_dict_format())

    def get_dict_format(self):
        return {
            'rid': self.rid,
            'cmd': self.cmd,
            'timeout': self.timeout,
            'expire': self.expire,
            'target_path': self.target_path,
            'echo_path': self.echo_path,
            'payload': dict(self.payload, **self.kwargs)
        }

    def dump(self):
        print("Request")
        print('=' * 20)
        for key, value in self.get_dict_format().items():
            print(key, ':', value)
        print('')

    def send(self):
        """发送请求"""
        payload_object = self.get_dict_format()
        status, _, reason = rpush(self.target_path, payload_object)
        self._sent_tsp = time.time()
        if status != OK:
            self._sent_fail_reason = reason

        return self

    def publish(self):
        """发送请求"""
        payload_object = self.get_dict_format()
        status, _, reason = rpublish(self.target_path, payload_object)
        self._sent_tsp = time.time()
        if status != OK:
            self._sent_fail_reason = reason

        return self

    def wait_response(self):
        """等待应答"""
        if self._sent_tsp is None:
            self.send()

        if self._sent_fail_reason:
            return IncorrectResponse(self, reason=self._sent_fail_reason)

        result = None
        # TODO: 这个循环等待可能会导致大循环的明显延迟
        while result is None:
            status, result, reason = get(self.echo_path)
            if result is not None:
                break
            elif time.time() - self._sent_tsp > self.timeout:
                break
            else:
                time.sleep(0.05)

        if result is None:
            # 应答动作超时
            return IncorrectResponse(self, reason="远程应答超时")

        rid = result['rid']
        if rid != self.rid:
            pass

        return Response.load_response_from_json(self, result)

    @staticmethod
    def load_request_from_json(j):
        cmd = j['cmd']
        target_path = j['target_path']
        echo_path = j['echo_path']
        timeout = j['timeout']
        expire = j['expire']
        rid = j['rid']
        payload = j['payload']
        return Request(cmd, target_path, payload, echo_path, timeout, expire, rid)


"""-----------------------设备类 api-----------------------"""


def device_get_default(dev_type):
    """
    获取默认的设备对象
    :param dev_type: {{ DEVICE_TYPE_CODE }}
    :return:
        成功 OK, PlaneDevice, 'no error'
        失败 ERROR, None, reason
    """
    device = PlaneDefaultDevice.get_default(dev_type)
    if device:
        return return_ok_payload(device)
    else:
        return_error_payload("无法获取类型为{}的默认设备.".format(dev_type))


def device_set_default(dev_id):
    """
    将指定设备设置为默认设备
    :param dev_id: 设备id
    :return:
        成功 OK, PlaneDevice, 'no error'
        失败 ERROR, None, reason
    """
    device = PlaneDefaultDevice.set_default(dev_id)
    if device:
        return return_ok_payload(device)
    else:
        return_error_payload("无法将设备ID={}设为默认设备.".format(dev_id))


def device_get_yc(dev_type):
    """
    获取指定设备类型的遥测数据
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    yc_path = profile.get_device_yc_path(dev_type)
    return lindex(yc_path, -1)


def device_get_yx(dev_type):
    """
    获取指定设备类型的遥测数据
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    yx_path = profile.get_device_yx_path(dev_type)
    return lindex(yx_path, -1)


def device_get_control_command(dev_type):
    """
    获取设备控制命令
    ：:return
        成功 OK, command, 'no error'
        失败 ERROR, None, reason
    """
    control_path = profile.get_device_control_command_path(dev_type)
    status, command_json, reason = lpop(control_path)
    if status != OK:
        return return_error_payload(reason)

    if command_json is None:
        return return_warning_payload(reason)

    try:
        command = Request.load_request_from_json(command_json)
    except KeyError as e:
        return return_error_payload(E_KEY_ERROR, msg=str(e))

    return return_ok_payload(command)


def device_get_control_command_length(dev_type):
    """
    获取控制命令列表长度
    :return:
        成功 OK, int, 'no error'
        失败 ERROR, None, reason
    """
    control_path = profile.get_device_control_command_path(dev_type)
    return llen(control_path)


def device_get_yt(dev_type):
    """
    获取指定设备类型的遥调数据
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    return device_get_control_command(dev_type)


def device_get_yk(dev_type):
    """
    获取指定设备类型的遥控数据
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    return device_get_control_command(dev_type)


def device_get_profile(dev_type):
    """
    获取指定设备类型的配置数据
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    profile_path = profile.get_device_profile_path(dev_type)
    return get(profile_path)


def device_set_profile_statement(dev_type, statement, expire=None):
    """
    获取指定设备类型的配置数据
    为保证设备配置数据的时效性，设备配置数据有效时间应设定在一定的范围内，默认为5秒
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :param statement: dict
    :param expire: 过期时间
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    if expire is None:
        expire = profile.KEY_EXPIRE

    profile_path = profile.get_device_profile_path(dev_type)
    return rset(profile_path, statement, ex=expire)


def device_set_data_registers(dev_type, registers):
    """
    推送设备的数据寄存器
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :param registers: dict
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    path = profile.get_device_yc_path(dev_type)
    return rpush(path, registers)


def device_set_hold_registers(dev_type, registers):
    """
    推送设备的保持寄存器
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :param registers: dict
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    path = profile.get_device_control_path(dev_type)
    return rpush(path, registers)


def device_control(dev_type, function, args):
    """
    获取指定设备类型的配置数据
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :param function: 设备函数
    :param args: 函数参数
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    device_control_path = profile.get_device_control_command_path(dev_type)
    payload = {
        'function': function,
        'args': args
    }
    request = Request('control', device_control_path, payload)
    r = profile.public_redis
    response = request.publish().wait_response()

    return response.pairs()


def device_set_yt(dev_type, key, value):
    """
    设置设备遥调值
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    return device_control(dev_type, key, value)


def device_set_yk(dev_type, key, value):
    """
    设置设备遥控值
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    return device_control(dev_type, key, value)


def device_get_list_by_type(dev_type):
    """
    获取指定类型的设备列表
    :param dev_type:
    :param dev_type:  {{ DEVICE_TYPE_CODE }}
    :return:
        成功 OK, list, 'no error'
        失败 ERROR, None, reason
    """
    target_dev_type = PlaneDeviceType.objects.get(code=dev_type)
    all_dev = PlaneDevice.objects.filter(type=target_dev_type)
    return return_ok_payload(all_dev)


def device_get_driver_by_id(dev_id):
    """
    根据设备ID获取设备
    :param dev_id: device id
    :return:
        成功 OK, PlaneDevice, 'no error'
        失败 ERROR, None, reason
    """


"""-----------------------流程类 api-----------------------"""


def flow_get_status_from_cache():
    """
    从缓存获取流程状态
    直接通过get指令从redis缓存中读取流程状态的数据并返回，一般用于显示用。
    若要获得精准的状态应该使用：@flow_get_status_from_root
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    flow_status_path = profile.get_flow_status_path()
    return get(flow_status_path)


def flow_update_status(status):
    """
    更新流程状态
    一般用于flowd进程，作用是将当前流程运行的状态以一定的周期（默认是3秒）用set指令写入redis缓存中
    :return:
        成功 OK, None, 'no error'
        失败 ERROR, None, reason
    """
    flow_status_path = profile.get_flow_status_path()
    return rset(flow_status_path, status)


def flow_update_source(source):
    """
    更新流程源码
    一般用于flowd进程，作用是将当前正在执行的全部流程源文件内容写入redis缓存中，
    写入时机是流程开始运行前（收到执行流程指令并确认后）
    :return:
        成功 OK, None, 'no error'
        失败 ERROR, None, reason
    """
    flow_source_path = profile.get_flow_source_context_path()
    return rset(flow_source_path, source)


def flow_get_control_command():
    """
    获取流程控制命令
    一般用于flowd从redis缓存中获取其他进程对流程运行的控制指令，
    例如，开始（run），停止（stop），状态（status）等
    ：:return
        成功 OK, command, 'no error'
        失败 ERROR, None, reason
    """
    flow_control_path = profile.get_flow_control_path()
    status, command_json, reason = lpop(flow_control_path)
    if status != OK:
        return return_error_payload(reason)

    if command_json is None:
        return return_warning_payload(reason)

    try:
        command = Request.load_request_from_json(command_json)
    except KeyError as e:
        return return_error_payload(E_KEY_ERROR, msg=str(e))

    return return_ok_payload(command)


def flow_get_control_command_length():
    """
    获取控制命令列表长度
    :return:
        成功 OK, int, 'no error'
        失败 ERROR, None, reason
    """
    flow_control_path = profile.get_flow_control_path()
    return llen(flow_control_path)


def flow_get_status_from_root():
    """
    给flowd发送一条获取状态的指令
    通过向flowd进程发送status指令获取精准的流程运行状态，这个接口的数据传输、等待成本较高，
    若对状态的精准性要求不高可以调用接口：@flow_get_status_from_cache，直接从缓存获取。
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    flow_control_path = profile.get_flow_control_path()
    request = Request('status', flow_control_path, payload={})
    response = request.publish().wait_response()

    return response.pairs()


def flow_run(prj_id, flow_id):
    """
    运行流程
    给flowd发送一条运行流程的指令
    :param prj_id: 项目ID
    :param flow_id: 流程id
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get_current()
    if status != OK:
        return return_error_payload(reason)

    if project.id != prj_id:
        return return_error_payload('不允许未执行的项目启动流程，当前执行的项目ID={}'.format(project.id))

    payload = {
        'prj_id': prj_id,
        'flow_id': flow_id,
    }
    flow_control_path = profile.get_flow_control_path()
    request = Request('run', flow_control_path, payload=payload)
    response = request.publish().wait_response()

    return response.pairs()


def flow_stop():
    """
    停止流程
    给flowd发送一条停止运行流程的指令
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    flow_control_path = profile.get_flow_control_path()
    request = Request('stop', flow_control_path, payload={})
    response = request.publish().wait_response()

    return response.pairs()


def flow_save(flow_file_path, name):
    """
    将流程保存到系统目录里
    :return:
        成功 OK, FlowFile, 'no error'
        失败 ERROR, None, reason
    """
    loader = flowex.FlowLoader()
    status, src_obj, reason = loader.load_source_from_abs_path(name, flow_file_path)
    if status != OK:
        return return_error_payload(reason)

    status, flow_obj, reason = src_obj.compile()
    if status != OK:
        return return_error_payload(reason)

    flow = FlowFile(name=name, origin_path=flow_file_path)
    flow.save()

    flow.clone_flow_file_from_path(flow_file_path)

    return return_ok_payload(flow)


def flow_update(fid, flow_file_path):
    """
    更新流程文件
    :param fid: 流程文件ID
    :param flow_file_path: 新的文件路径
    :return:
        成功 OK, FlowFile, 'no error'
        失败 ERROR, None, reason
    """
    try:
        flow = FlowFile.objects.get(id=fid)
    except FlowFile.DoesNotExist:
        return return_error_payload('不存在id={}的流程文件'.format(fid))

    flow.clone_flow_file_from_path(flow_file_path)
    return return_ok_payload(flow)


"""-----------------------项目类 api-----------------------
    项目管理遵循一定的约束：
    1. 系统中最多允许存在一个正在执行的项目
    2. 若没有指定项目ID，则所有操作都指向当前激活的项目
    3. 若出现状态冲突必须人工处理
"""


def project_get_current():
    """
    获取当前激活状态的项目
    从redis中获取当前处于激活状态的项目id
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    project_set = Project.objects.filter(status=profile.PRJ_STATUS_RUNNING)

    if len(project_set) > 1:
        reason_items = ["项目{}状态出现冲突:"]
        for project in project_set:
            reason_items.append('<{}>  <{}>'.format(project.id, project.name))
        return return_error_payload(reason='\n'.join(reason_items))

    if len(project_set) == 0:
        reason = "没有处于运行状态的项目"
        return return_ok_payload(None, reason)

    project = project_set[0]
    return return_ok_payload(project)


def project_create(prj_name, sn=None, subscript=None, description=None, comment=None):
    """
    创建新的项目
    :param prj_name: 项目名称
    :param sn: 实验室内部的项目编码
    :param subscript: 项目摘要
    :param description: 项目介绍
    :param comment: 备注
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    if sn is None:
        sn = '无'

    if subscript is None:
        subscript = ''

    if description is None:
        description = ''

    if comment is None:
        comment = '创建项目'

    prj = Project(name=prj_name, sn=sn, subscript=subscript, description=description, status=profile.PRJ_STATUS_INIT)
    prj.save()

    prj.set_status(profile.PRJ_STATUS_CONFIGURE, comment)

    return return_ok_payload(prj)


def project_get(prj_id):
    """
    获取项目信息
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    try:
        project = Project.objects.get(id=prj_id)
        return return_ok_payload(project)
    except Project.DoesNotExist:
        return return_error_payload("没有找到ID={}的项目".format(prj_id))


def project_modify_status(prj_id, new_status, comment):
    """
    更改项目状态, 不需要经过状态转移验证
    :param prj_id: 项目ID
    :param new_status: 新的项目状态
    :param comment: 更新说明
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    if new_status not in profile.PROJECT_STATUS_LIST:
        return return_error_payload("新状态{}无效, 有效列表[{}]".format(new_status, ','.join(profile.PROJECT_STATUS_LIST)))

    status, project, reason = project_get(prj_id)
    if status != OK:
        return return_error_payload(reason)

    reason = "强制更改项目状态时必须提供原因说明。"
    if isinstance(comment, str) is False:
        return return_error_payload(''.join([reason, '(备注类型不符)']))
    elif len(comment) == 0:
        return return_error_payload(''.join([reason, '(不能提供空备注)']))

    plog.warn("** 强制更改项目<name={}, id={}>状态, 从<{}>变更为<{}>".
              format(project.name, project.id, project.status, new_status))

    history = ProjectStateLog(project=project, old_status=project.status, new_status=new_status, comment=str(comment))
    history.save()

    project.status = new_status
    project.save()

    return return_ok_payload(project)


def project_update_status(prj_id, new_status, comment):
    """
    更新项目状态
    :param prj_id: 项目id
    :param new_status: 新的项目状态
    :param comment: 更新说明
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get(prj_id)
    if status != OK:
        return return_error_payload(reason)
    if project is None:
        return return_error_payload(reason)

    if new_status not in profile.PROJECT_STATUS_LIST:
        reason = '不支持的状态<{}, 支持的状态是: <{}>'.format(new_status, ', '.join(profile.PROJECT_STATUS_LIST))
        return return_error_payload(reason)

    if project.status == new_status:
        return return_ok_payload(project)

    next_status_list = profile.PROJECT_STATUS_CHANGE_ROUTE[project.status]
    if new_status not in next_status_list:
        reason = '项目状态不能从<{}>转移为<{}>,支持的转移状态为:<{}>'.\
            format(project.status, new_status, ', '.join(next_status_list))
        return return_error_payload(reason)

    history = ProjectStateLog(project=project, old_status=project.status, new_status=new_status, comment=str(comment))
    history.save()

    project.status = new_status
    project.save()

    return return_ok_payload(project)


def project_switch_to_ready_status(prj_id):
    """
    项目配置完成，进行项目状态的切换，由配置阶段转换为就绪状态
    此时项目状态必须是配置状态，且绑定设备至少有一个
    :param prj_id: 项目ID
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    return project_update_status(prj_id, profile.PRJ_STATUS_READY, '状态自动转移')


def project_switch_to_running_status(prj_id):
    """
    项目状态切换为执行，进行项目状态的切换
    :param prj_id: 项目ID
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    _, project, reason = project_get_current()

    if project:
        reason = '项目{}, id={}已经在执行中'.format(project.name, project.id)
        return return_error_payload(reason)

    status, prj, reason = project_update_status(prj_id, profile.PRJ_STATUS_RUNNING, '状态自动转移')
    if status == OK:
        project_services_start(prj_id)
        return return_ok_payload(prj, reason)
    else:
        return return_error_payload(reason)


def project_switch_to_pause_status(prj_id):
    """
    将项目切换到暂停状态
    :param prj_id: 项目ID
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    project_service_stop(prj_id)
    return project_update_status(prj_id, profile.PRJ_STATUS_PAUSE, '状态自动转移')


def project_switch_to_abort_status(prj_id):
    """
    将项目切换到中止状态
    :param prj_id: 项目ID
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    project_service_stop(prj_id)
    return project_update_status(prj_id, profile.PRJ_STATUS_ABORT, '状态自动转移')


def project_switch_to_done_status(prj_id):
    """
    将项目切换到完成状态
    :param prj_id: 项目ID
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    project_service_stop(prj_id)
    return project_update_status(prj_id, profile.PRJ_STATUS_DONE, '状态自动转移')


def project_services_start(prj_id):
    """
    启动项目相关的服务程序,
    只允许启动处于执行状态的项目
    :return:
        成功 OK, list, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get_current()
    if status != OK:
        return return_error_payload(reason)
    if project is None:
        return return_error_payload(reason)

    if prj_id != project.id:
        return return_error_payload("当前执行的项目和给定项目ID不匹配")

    device_list = project.get_depended_device_list()
    if len(device_list) == 0:
        reason = '还没有给项目<{}>, id={}指定关联设备'.format(project.name, project.id)
        return return_error_payload(reason, None)

    for device in device_list:
        dev_uuid = device.ps_uuid
        command_item = [profile.python_executable_path, profile.device_driver_manager_script,
                        '--run', '--dev-id', str(device.id), '-g', device.type.name, '--uuid', dev_uuid]
        commandline = ' '.join(command_item)
        pid = plane.create_process(dev_uuid, commandline, profile.platform_root_dir)
        if pid <= 0:
            reason = '项目<{}, id={}>驱动<name={}, code={}, uuid={}>启动失败！'.\
                format(project.name, project.id, device.type.name, device.type.code, device.ps_uuid)
            plog.warn(reason)

    return project_service_status(prj_id)


def project_service_stop(prj_id):
    """
    停止项目相关的服务程序
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get_current()
    if status != OK:
        return return_error_payload(reason, None)
    if project is None:
        return return_error_payload(reason)

    if prj_id != project.id:
        return return_error_payload("当前执行的项目和给定项目ID不匹配")

    device_list = project.get_depended_device_list()
    if len(device_list) == 0:
        reason = '还没有给项目<{}>, id={}指定关联设备'.format(project.name, project.id)
        return return_error_payload(reason, None)

    for device in device_list:
        dev_uuid = device.ps_uuid
        pid = plane.get_process_pid(dev_uuid)
        if pid > 0:
            if plane.stop_process(dev_uuid, pid) > 0:
                reason = '项目<{}, id={}>驱动<name={}, code={}, uuid={}, pid={}>停止失败！'. \
                    format(project.name, project.id, device.type.name, device.type.code, device.ps_uuid, pid)
                plog.warn(reason)

    return project_service_status(prj_id)


def project_service_restart(prj_id):
    """
    重启项目相关的服务程序
    :return:
        成功 OK, dict, 'no error'
        失败 ERROR, None, reason
    """
    status, _, reason = project_service_stop(prj_id)
    if status != OK:
        return return_error_payload(reason, None)

    return project_services_start(prj_id)


def project_service_status(prj_id):
    """
    获取项目相关的服务状态
    :return:
        成功 OK, list, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get_current()
    if status != OK:
        return return_error_payload(reason)
    if project is None:
        return return_error_payload(reason)

    if prj_id != project.id:
        return return_error_payload("当前执行的项目和给定项目ID不匹配")

    device_list = project.get_depended_device_list()
    if len(device_list) == 0:
        reason = '还没有给项目<{}>, id={}指定关联设备'.format(project.name, project.id)
        return return_error_payload(reason, None)

    process_status = list()
    for device in device_list:
        dev_uuid = device.ps_uuid
        pid = plane.get_process_pid(dev_uuid)
        if pid > 0:
            status = {
                '服务中': True,
                'pid': pid,
                'uuid': dev_uuid,
                'device': device.id,
                'dev_type': device.type.code,
                'dev_name': device.type.name,
            }
        else:
            status = {
                '服务中': False,
                'pid': -1,
                'uuid': dev_uuid,
                'device': device.id,
                'dev_type': device.type.code,
                'dev_name': device.type.name,
            }
        process_status.append(status)

    return return_ok_payload(process_status)


def project_register_device(prj_id, dev_id):
    """
    给项目注册设备
    每个项目针对某种设备只接受一个型号
    :param prj_id: 项目ID
    :param dev_id: 设备ID
    :return:
        成功 OK, PlaneDevice, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get(prj_id)
    if status != OK:
        return return_error_payload(reason)

    try:
        device = PlaneDevice.objects.get(id=dev_id)
    except PlaneDevice.DoesNotExist:
        return return_error_payload("没有找到ID={} 的设备".format(dev_id))

    # 避免重复注册同一类设备
    for t in project.get_depended_device_list():
        if t.type.code == device.type.code:
            reason = "项目<{}>已经注册过<{}>类型的设备,设备ID={}".format(project.name, device.type.name, t.id)
            return return_error_payload(reason)

    form = ProjectWithDevice(project=project, device=device)
    form.save()

    return return_ok_payload(device)


def project_unregister_device(prj_id, dev_id):
    """
    给项目注销设备
    每个项目针对某种设备只接受一个型号
    :param prj_id: 项目ID
    :param dev_id: 设备ID
    :return:
        成功 OK, PlaneDevice, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get(prj_id)
    if status != OK:
        return return_error_payload(reason)

    try:
        device = PlaneDevice.objects.get(id=dev_id)
    except PlaneDevice.DoesNotExist:
        return return_error_payload("没有找到ID={} 的设备".format(dev_id))

    form = ProjectWithDevice.objects.filter(project=project, device=device)
    if len(form) == 0:
        return return_error_payload("项目<{}>没有绑定设备<{}/{}>".format(project.name, device.type.name, device.id))

    form.delete()
    return return_ok_payload(device)


def project_get_device_by_type(prj_id, dev_type):
    """
    根据设备类型，获取设备id
    :param prj_id: 项目ID
    :param dev_type: 设备类型代码
    :return:
        成功 OK, PlaneDevice, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get(prj_id)
    if status != OK:
        return return_error_payload(reason)

    for device in project.get_depended_device_list():
        if device.type.code == dev_type:
            return return_ok_payload(device)

    return return_error_payload("项目<{}>没有找到类型代码为：<{}> 的关联设备".format(project.name, dev_type))


def project_get_depend_devices_list(prj_id):
    """
    根据设备ID获取关联的设备列表
    :param prj_id: 项目id
    :return:
        成功 OK, list, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get(prj_id)
    if status != OK:
        return return_error_payload(reason)

    return return_ok_payload(project.get_depended_device_list())


def project_list():
    """
    获取全部的项目
    :return:
        成功 OK, Project dict list, 'no error'
        失败 ERROR, [], reason
    """
    configure_list = Project.objects.filter(status=profile.PRJ_STATUS_CONFIGURE)
    ready_list = Project.objects.filter(status=profile.PRJ_STATUS_READY)
    pause_list = Project.objects.filter(status=profile.PRJ_STATUS_PAUSE)
    running_list = Project.objects.filter(status=profile.PRJ_STATUS_RUNNING)

    return return_ok_payload({
        profile.PRJ_STATUS_CONFIGURE: configure_list,
        profile.PRJ_STATUS_READY: ready_list,
        profile.PRJ_STATUS_PAUSE: pause_list,
        profile.PRJ_STATUS_RUNNING: running_list
    })


def project_filter_by_status(status):
    """
    根据提供的状态过滤项目
    :param status: 项目状态
    :return:
        成功 OK, Project list, 'no error'
        失败 ERROR, [], reason
    """
    return return_ok_payload(Project.objects.filter(status=status))


def project_list_configure():
    """
    获取全部的项目且状态是配置
    :return:
        成功 OK, Project list, 'no error'
        失败 ERROR, None, reason
    """
    return project_filter_by_status(profile.PRJ_STATUS_CONFIGURE)


def project_list_ready():
    """
    获取全部的项目且状态是就绪
    :return:
        成功 OK, Project list, 'no error'
        失败 ERROR, None, reason
    """
    return project_filter_by_status(profile.PRJ_STATUS_READY)


def project_list_running():
    """
    获取全部的项目且状态是执行
    :return:
        成功 OK, Project list, 'no error'
        失败 ERROR, None, reason
    """
    return project_filter_by_status(profile.PRJ_STATUS_RUNNING)


def project_list_pause():
    """
    获取全部的项目且状态是暂停
    :return:
        成功 OK, Project list, 'no error'
        失败 ERROR, None, reason
    """
    return project_filter_by_status(profile.PRJ_STATUS_PAUSE)


def project_list_done():
    """
    获取全部的项目且状态是完成
    :return:
        成功 OK, Project list, 'no error'
        失败 ERROR, None, reason
    """
    return project_filter_by_status(profile.PRJ_STATUS_DONE)


def project_list_abort():
    """
    获取全部的项目且状态是中止
    :return:
        成功 OK, Project list, 'no error'
        失败 ERROR, None, reason
    """
    return project_filter_by_status(profile.PRJ_STATUS_ABORT)


def project_get_statement_change_history(prj_id):
    """
    获取项目状态改变的历史
    :return:
        成功 OK, list, 'no error'
        失败 ERROR, None, reason
    """
    status, project, reason = project_get(prj_id)
    if status != OK:
        return return_error_payload(reason)

    return return_ok_payload(ProjectStateLog.objects.filter(project=project))


def project_list_flow_file(prj_id):
    """
    获取项目的流程文件列表
    :param prj_id: 项目id
    :return:
        成功 OK, list(FlowFile), 'no error'
        失败 ERROR, None, reason
    """
    try:
        project = Project.objects.get(id=prj_id)
    except Project.DoesNotExist:
        return return_error_payload("id={}的项目不存在".format(prj_id))

    return return_ok_payload([pf.flow for pf in ProjectWithFlow.objects.filter(project=project)])


def project_save_flow_file(prj_id, flow_file_path, name, comment):
    """
    将流程文件保存起来
    :param prj_id: 项目id
    :param flow_file_path: 流程文件路径
    :param name: 希望将流程文件保存的名称
    :param comment: 对这个流程文件的备注说明
    :return:
        成功 OK, FlowFile, 'no error'
        失败 ERROR, None, reason
    """
    # 检查文件是否合格
    loader = flowex.FlowLoader()
    status, src_obj, reason = loader.load_source_from_abs_path(name, flow_file_path)
    if status != OK:
        return return_error_payload(reason)

    status, flow_obj, reason = src_obj.compile()
    if status != OK:
        return return_error_payload(reason)

    try:
        project = Project.objects.get(id=prj_id)
    except Project.DoesNotExist:
        return return_error_payload("id={}的项目不存在".format(prj_id))

    flow = FlowFile(name=name, origin_path=flow_file_path)
    flow.save()

    flow.clone_flow_file_from_path(flow_file_path)

    pf = ProjectWithFlow(project=project, flow=flow, comment=comment)
    pf.save()

    return return_ok_payload(flow)


def project_bind_flow_file(prj_id, flw_id):
    """
    将系统里现有的流程文件和项目进行绑定
    :param prj_id: 项目id
    :param flw_id: 流程文件id
    :return:
        成功 OK, True, 'no error'
        失败 ERROR, False, reason
    """
    try:
        pf = ProjectWithFlow.objects.get(project=prj_id, flow=flw_id)
    except ProjectWithFlow.DoesNotExist:
        pf = None

    if pf:
        return return_ok_payload(True)

    try:
        project = Project.objects.get(id=prj_id)
        flow = FlowFile.objects.get(id=flw_id)
    except (Project.DoesNotExist, FlowFile.DoesNotExist):
        return return_error_payload("没有找到id={}的项目或id={}的流程".format(prj_id, flw_id), False)

    pf = ProjectWithFlow(project=project, flow=flow, comment="事后绑定")
    pf.save()

    return return_ok_payload(True)


def project_unbind_flow_file(prj_id, flw_id):
    """
    将流程文件和项目解除绑定
    :param prj_id: 项目id
    :param flw_id: 流程id
    :return:
        成功 OK, None, 'no error'
        失败 ERROR, None, reason
    """
    try:
        pf = ProjectWithFlow.objects.get(project=prj_id, flow=flw_id)
    except ProjectWithFlow.DoesNotExist:
        return return_error_payload("id={}的项目中不包含id={}的流程文件".format(prj_id, flw_id))

    pf.delete()
    return return_ok_payload()


def project_clone(prj_id):
    """
    将一个项目克隆
    克隆项目的配置信息，包含名称（名称后附加`-clone`字样），设备绑定信息，流程文件绑定信息
    注意：
        克隆后新项目的状态和来源项目的状态保持一致，因此若对项目的状态有更改需求的话需要手动调用
        project_modify_status去强制更改。
    :param prj_id:
    :return:
        成功 OK, Project, 'no error'
        失败 ERROR, None, reason
    """
    try:
        origin = Project.objects.get(id=prj_id)
    except Project.DoesNotExist:
        return return_error_payload("没有找到id={}的项目".format(prj_id))

    # 原始项目绑定的设备列表
    device_with_origin = ProjectWithDevice.objects.filter(project=origin)

    # 原始项目绑定的流程列表
    flow_with_origin = ProjectWithFlow.objects.filter(project=origin)

    # 项目对象
    project = Project()
    project.name = ''.join([origin.name, '-clone'])
    project.sn = origin.sn
    project.subscript = origin.subscript
    project.description = origin.description
    project.status = project.status

    # 项目状态记录
    ps = ProjectStateLog()
    ps.project = project
    ps.old_status = '初始化'
    ps.new_status = project.status
    ps.comment = "因克隆项目{}进行状态自动切换".format(prj_id)

    # 初始化项目绑定设备列表
    device_with_project = list()
    for device in device_with_origin:
        dwp = ProjectWithDevice()
        dwp.project = project
        dwp.device = device
        device_with_project.append(dwp)

    # 初始化项目绑定流程列表
    flow_with_project = list()
    for flow in flow_with_origin:
        fwp = ProjectWithFlow()
        fwp.project = project
        fwp.flow = flow
        fwp.comment = flow.comment
        flow_with_project.append(flow)

    # 保存
    try:
        project.save()
        ps.save()

        for dwp in device_with_project:
            dwp.save()

        for fwp in flow_with_project:
            fwp.save()
    except Exception as e:
        for dwp in device_with_project:
            if dwp.id:
                dwp.delete()

        for fwp in flow_with_project:
            if fwp.id:
                fwp.delete()

        if ps.id:
            ps.delete()

        if project.id:
            project.delete()

        return return_error_payload("clone project{}".format(prj_id) + str(e))

    return return_ok_payload(project)


"""         全局消息广播API            """


def broadcast_info(title, txt):
    """
    广播信息
    :return:
        成功 OK, None, 'no error'
    """
    msg = Message(type='info', title=title, show_count=1, txt=txt)
    msg.save()
    return return_ok_payload(msg)


def broadcast_warn(title, txt):
    """
    广播警告
    :return:
        成功 OK, None, 'no error'
    """
    msg = Message(type='warn', title=title, show_count=1, txt=txt)
    msg.save()
    return return_ok_payload(msg)


def broadcast_error(title, txt):
    """
    广播错误
    :return:
        成功 OK, None, 'no error'
    """
    msg = Message(type='error', title=title, show_count=1, txt=txt)
    msg.save()
    return return_ok_payload(msg)


"""         数据记录清除API            """


def purge_project():
    """
    清理项目数据库，
    注意：慎重使用这个函数
    :return:
        成功 OK, None, 'no error'
    """

    # 删除项目状态数据库记录
    ProjectStateLog.objects.all().delete()

    # 删除项目关联设备记录
    ProjectWithDevice.objects.all().delete()

    # 删除项目记录
    Project.objects.all().delete()

    return return_ok_payload(None)


def purge_device():
    """
    清除设备相关的数据库
    :return:
        成功 OK, None, 'no error'
    """

    # 删除项目关联设备记录
    ProjectWithDevice.objects.all().delete()

    # 删除设备历史记录
    PlaneDeviceHistory.objects.all().delete()

    # 删除设备记录
    PlaneDevice.objects.all().delete()

    return return_ok_payload(None)


"""        进程控制相关API      """


def process_create(executable, args, cwd):
    """
    根据给定的可执行程序创建进程
    :param executable: 可执行文件路径
    :param args: 参数列表
    :param cwd: 工作目录
    :return:
        成功 OK, list, 'no error'
        失败 ERROR, None, reason
    """
    try:
        args.insert(0, executable)
        payload = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    except Exception as e:
        return return_error_payload(reason=str(e))

    return return_ok_payload(payload)


class PeriodController:
    """
        运行周期控制器

        # 初始化
        controller = PeriodController(period_in_ms=1000)

        # 周期控制
            控制循环开始{{
                # 放在第一句执行，确保控制器在每个循环里都能运行一次
                controller.probe_period_delay()

                # 下面放其他代码
                #  .....
            }} 控制循环结束
    """
    class Binder:
        def __init__(self, cb, times, *args, **kwargs):
            # 指明经过多少个周期后进行调用
            self._times = times
            self.times = times
            self.cb = cb
            self.args = args
            self.kwargs = kwargs

        def reset_times(self):
            self.times = self._times

        def __call__(self, *args, **kwargs):
            return self.cb(*self.args, **self.kwargs)

    def __init__(self, period_in_ms):
        self.period_in_ms = period_in_ms
        self.period_in_seconds = period_in_ms/1000.0
        self.real_period_in_seconds = period_in_ms/1000.0
        self.last_tsp = 0

        # 休眠微调值， 范围 -10ms <= v <= 10ms
        self.micro_offset = 0

        # 函数注册点，用于快速搜索
        self._callback = list()
        # 参数保存点，用于存放回调及参数
        self._binder = list()

    def bind(self, cb, times=None, *args, **kwargs):
        """绑定周期回调函数"""
        try:
            _ = self._callback.index(cb)
        except ValueError:
            self._callback.append(cb)
            times = 1 if times is None else int(times)
            self._binder.append(PeriodController.Binder(cb, times, *args, **kwargs))
        return self

    def notify_all_binder(self):
        """通知所有绑定的监听函数"""
        for binder in self._binder:
            binder.times -= 1
            if binder.times > 0:
                continue

            binder.reset_times()
            binder()

        return self

    def set_period(self, period_in_ms):
        """重新配置控制器，并重新开始控制周期"""
        self.last_tsp = 0
        self.period_in_ms = period_in_ms
        self.period_in_seconds = period_in_ms/1000.0

    def get_period(self):
        """获取控制器的控制周期值，单位是毫秒"""
        return self.period_in_ms

    def get_real_period(self):
        """获取控制器的控制测量周期值，单位是毫秒"""
        return round(self.real_period_in_seconds * 1000)

    def reset(self):
        """复位控制器，重新开始控制周期"""
        self.set_period(self.period_in_ms)

    def probe_period_delay(self):
        """
        周期延迟探测器

        if 前一次执行时间 == 0:
            前一次执行时间 = 当前时间
            return
        end if

        本次时间间隔 = 当前时间 — 前一次执行时间
        时间提前量 = 周期设定值 - 本次时间间隔

        if 时间提前量 > 0:
            sleep 时间提前量
        end if

        period running here.
        """
        now = time.time()

        if self.last_tsp == 0:
            self.last_tsp = now
            return self

        interval_in_seconds = now - self.last_tsp
        interval_delta_in_seconds = self.period_in_seconds - interval_in_seconds

        # 小于5毫秒则认为时间到了
        if interval_delta_in_seconds > 0.005:
            time.sleep(interval_delta_in_seconds)

        now = time.time()
        self.real_period_in_seconds = now - self.last_tsp
        self.last_tsp = now

        return self.notify_all_binder()
