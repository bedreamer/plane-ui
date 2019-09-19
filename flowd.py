# -*- coding: utf-8 -*-
import codecs
import time
import os
import sys
import json
import profile
import plog
import signal
import flowex
import api
import re
from storage.models import *

'''
class FlowObject:
    """单步流程对象"""
    def get_status_map(self):
        return {
            '当前流程名': self.name,
            '流程循环计数': len(self),
            '本次循环开始时戳': self.get_cuurent_begin_tsp(),
            '本次循环开始时间': self.get_current_begin_time(),
            '本次循环时长': self.get_current_running_seconds(),
            '当前判断条件': self.get_conditions_as_string(),
            'Source True 跳转': self.true_jump_name,
            'Source False 跳转': self.false_jump_name,
            'Source': json.dumps(self.source, ensure_ascii=False),
        }


class PlaneFlow:
    def get_flow_status(self):
        """获取流程运行状态"""
        status = {
            "pid": os.getpid(),
            "工作目录": os.getcwd(),
            "流程运行状态": "运行中" if self.session else '未运行',
            '流程循环周期': self.main_period_controller.get_period(),
            '流程动态周期': self.main_period_controller.get_real_period(),
        }
        if self.session:
            active_status = self.session.get_status_map()
            status = dict(status, **active_status)

        return status
'''


class FlowSession(object):
    """流程会话基类"""
    def __init__(self, srv, born):
        self.srv = srv
        self.born = born
        self.loop = 0

    def get_status_map(self):
        status_map = {
            '流程启动时间': time.strftime(profile.DT_FORMAT, time.localtime(self.born)),
            '流程激活总时长': time.time() - self.born,
            '流程总循环次数': self.loop
        }
        source_status = self.source.get_status_map()
        executor_status = self.executor.get_status_map()
        return dict(executor_status, **source_status, **status_map)

    def process_with_request(self, request):
        """处理请求"""
        if request.is_expire():
            return self.on_expired_command(request)

        cmd = request.cmd
        callback_function = self.__getattribute__(''.join(['on_', cmd]))
        callback = self.on_not_supported_command if not callback_function else callback_function
        return callback(request)

    @staticmethod
    def on_not_supported_command(request):
        return api.IncorrectResponse(request, reason="不支持的命令").do_response()

    @staticmethod
    def on_expired_command(request):
        plog.warn("接收到过期的命令：", command=str(request))

    def get_status(self):
        raise NotImplementedError

    def on_status(self, request):
        status = self.get_status()
        return api.CorrectResponse(request, status).do_response()

    @staticmethod
    def on_exit(request):
        return api.CorrectResponse(request).do_response()

    def run_step_forward(self):
        self.loop += 1


class FlowIdleSession(FlowSession):
    """空闲会话管理器"""
    def get_status(self):
        return {
            "pid": os.getpid(),
            "工作目录": os.getcwd(),
            "流程运行状态": '未运行',
        }

    def on_run(self, request):
        flow_id = request.payload['flow_id']
        prj_id = request.payload['prj_id']

        try:
            flow = FlowFile.objects.get(id=flow_id)
        except FlowFile.DoesNotExist:
            return api.IncorrectResponse(request, reason="没有找到id={}的流程".format(flow_id)).do_response()

        flow_file_abs_path = flow.get_flow_file_as_abs_path()

        loader = flowex.FlowLoader()
        status, src_obj, reason = loader.load_source_from_abs_path(flow.name, flow_file_abs_path)
        if status != api.OK:
            return api.IncorrectResponse(request, reason=reason).do_response()

        status, flow_obj, reason = src_obj.compile()
        if status != api.OK:
            return api.IncorrectResponse(request, reason=reason).do_response()

        status, _, reason = flow_obj.link()
        if status != api.OK:
            return api.IncorrectResponse(request, reason=reason).do_response()

        self.srv.startup_worker(prj_id, flow_id, loader, src_obj, flow_obj)
        return api.CorrectResponse(request).do_response()

    @staticmethod
    def on_stop(request):
        return api.IncorrectResponse(request, reason="流程还未执行").do_response()


class FlowWorkerSession(FlowSession):
    """执行中的流程管理器"""

    def __init__(self, srv, born, prj_id, flow_id, flow_loader, flow_source_object, flow_object):
        super().__init__(srv, born)
        self.prj_id = prj_id
        self.flow_id = flow_id
        self.flow_loader = flow_loader
        self.flow_source_object = flow_source_object
        self.flow_object = flow_object

        self.static_status = dict({
            "pid": os.getpid(),
            "工作目录": os.getcwd(),
            "流程运行状态": "运行中",
        }, **flow_source_object.get_status_map())

    def get_status(self):
        return dict(**self.static_status)

    @staticmethod
    def on_run(request):
        return api.IncorrectResponse(request, reason="流程正在执行中").do_response()

    def on_stop(self, request):
        self.srv.stop_worker()
        status = self.get_status()
        return api.CorrectResponse(request, status).do_response()

    def run_step_forward(self):
        live = self.flow_object.run()
        if live:
            return

        try:
            pwf = ProjectWithFlow.objects.get(project_id=self.prj_id, flow_id=self.flow_id)
            pwf.active = False
            pwf.save()
        except ProjectWithFlow.DoesNotExist:
            pass

        plog.info("流程执行结束")
        self.srv.stop_worker()


class FlowServer:
    def __init__(self):
        self.terminated = False
        self.born = time.time()
        self.pubsub = None
        self.session = None

    def make_subscriber(self):
        self.pubsub = profile.alloc_subscriber()
        self.pubsub.psubscribe(profile.get_flow_control_path())
        self.pubsub.psubscribe(profile.get_flow_status_path())

    def unsubscribe(self):
        # 退订所有频道
        self.pubsub.unsubscribe(None)

    def probe_flow_control_request(self):
        pack = self.pubsub.get_message(ignore_subscribe_messages=True, timeout=0.5)
        if not pack:
            return pack
        else:
            data = json.loads(pack['data'])
            return api.Request.load_request_from_json(data)

    def startup_worker(self, prj_id, flow_id, loader, src, flow):
        self.session = FlowWorkerSession(self, time.time(), prj_id, flow_id, loader, src, flow)

    def stop_worker(self):
        self.session = FlowIdleSession(self, self.born)

    def run_until_die(self):
        self.session = FlowIdleSession(self, self.born)
        self.make_subscriber()

        while not self.terminated:
            request = self.probe_flow_control_request()
            if request:
                self.session.process_with_request(request)
            self.session.run_step_forward()

        self.unsubscribe()
        print("flowd exited.")


if __name__ == '__main__':
    print("flowd running...")
    print("pid: {}".format(os.getpid()))
    print("cwd: {}".format(os.getcwd()))
    FlowServer().run_until_die()

