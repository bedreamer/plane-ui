# -*- coding: utf8 -*-
import profile
import json
import api

__doc__ = """流程控制指令集"""
__usage__ = __doc__ + """
Usage:
    flow [命令] [参数列表]
命令：
    run     执行流程文件
    stop    停止流程
    status  流程状态

启动流程：
    flow run {flow-file-name}
    eg. flow run 2.flow
停止流程：
    flow stop
流程状态：
    flow status"""


def flow_start(ctx, source):
    """执行流程文件"""
    status, project, reason = api.project_get_current()
    if status != api.OK:
        return
    if project is None:
        return

    if project.id < 0:
        print("当前还没有激活的项目，无法运行流程！")
        return

    status, payload, reason = api.flow_run(project.id, source)
    if status != api.OK:
        print(reason)
        return


def _dump_status_payload(payload):
    try:
        if isinstance(payload, str):
            _flow_status = json.loads(payload)
        else:
            _flow_status = payload
    except json.JSONDecodeError as e:
        print(e)
        return

    for key, value in _flow_status.items():
        print(key, ':', value)


def flow_stop(ctx):
    """停止流程"""
    # status, project, reason = api.project_get_current()
    # if status != api.OK:
    #     return
    #
    # if project is None:
    #     print("警告： 当前还没有激活的项目，无需停止流程！")
    #
    status, payload, reason = api.flow_stop()
    if status != api.OK:
        print(reason)
        return

    _dump_status_payload(payload)


def flow_status(ctx):
    """流程状态"""
    status, payload, reason = api.flow_get_status_from_root()
    if status != api.OK:
        print(reason)
        return

    _dump_status_payload(payload)


def main(ctx, cmd, *args):
    """执行流程"""
    if ctx.redis is None:
        print("** ERROR: 还没有连接")
        return

    if len(args) == 0:
        print("Usage:")
        print("  flow 【run|stop|status】 {参数}")
        return

    cmd = args[0].lower()
    if cmd == 'run':
        if len(args) != 2:
            print("Usage:")
            print("  flow run {source-file-name}")
            return
        return flow_start(ctx, args[1])
    elif cmd == 'stop':
        return flow_stop(ctx)
    elif cmd == 'status':
        return flow_status(ctx)
    else:
        print("unkown command: {}".format(' '.join(args)))
