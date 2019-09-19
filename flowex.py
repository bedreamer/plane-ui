# -*- coding: utf-8 -*-
# author: lijie
import re
import os
import codecs
import json
import time
import profile
import flowfile
import time
import api
import xlrd


class Instruction:
    """指令对象"""
    class Environment:
        def __init__(self):
            self.last_exe_tsp = 0
            self.running_count = 0

    def __init__(self, stage, period, target, function, args):
        self.stage = stage
        self.period = period
        self.target = target
        self.function = function
        self.args = args
        self._env = Instruction.Environment()

    def execute(self, flow):
        if self.period == 0:
            # 每次都执行
            pass
        elif self.period == -1 and self._env.last_exe_tsp == 0:
            # 仅执行一次
            pass
        elif time.time() - self._env.last_exe_tsp >= self.period:
            # 周期执行
            pass
        else:
            return

        status, _, reason = api.device_control(self.target, self.function, self.args)
        self._env.last_exe_tsp = time.time()
        self._env.running_count += 1

    def reset(self):
        self._env = Instruction.Environment()


class FlowUnitObject:
    """单步单元对象，流程执行的最小单元"""
    def __init__(self, name, inset_in, inset_running, inset_out, conditions, timeout, true_flow, false_flow):
        self.name = name
        self.inset_in = inset_in
        self.inset_running = inset_running
        self.inset_out = inset_out
        self.timeout = timeout
        self.true_flow = true_flow
        self.false_flow = false_flow

        self.conditions = conditions
        self.logic_conditions = list()

        # 本次激活的时间戳
        self.last_active_timestamp = 0
        # 本次检测结果和原因
        self.last_inspection_result = ''
        # 本次检测后的下一个目标流程
        self.last_target_flow = None

        logic_map = {
            '>': self.cmp_gt,
            '>=': self.cmp_ge,
            '<': self.cmp_lt,
            '<=': self.cmp_le,
            '==': self.cmp_eq,
            '!=': self.cmp_ne,
            '&&': self.cmp_and,
            '||': self.cmp_or,
        }

        def _preprocess_item(x):
            if isinstance(x, float) or isinstance(x, int) or x == 'self.loop':
                return x
            else:
                return x.split('.')

        if len(self.conditions) == 3:
            a, cmp, b = self.conditions
            item_a = _preprocess_item(a)
            item_cmp = logic_map[cmp]
            item_b = _preprocess_item(b)

            self.logic_conditions.append(item_a)
            self.logic_conditions.append(item_cmp)
            self.logic_conditions.append(item_b)
        elif len(self.conditions) == 7:
            a, cmp1, b, logic, c, cmp2, d = self.conditions

            item_a = _preprocess_item(a)
            item_cmp1 = logic_map[cmp1]
            item_b = _preprocess_item(b)

            item_c = _preprocess_item(c)
            item_cmp2 = logic_map[cmp2]
            item_d = _preprocess_item(d)

            self.logic_conditions.append(item_a)
            self.logic_conditions.append(item_cmp1)
            self.logic_conditions.append(item_b)

            self.logic_conditions.append(logic_map[logic])

            self.logic_conditions.append(item_c)
            self.logic_conditions.append(item_cmp2)
            self.logic_conditions.append(item_d)
        else:
            pass

        related_device_map = dict()
        for item in conditions:
            if isinstance(item, float) or isinstance(item, int) or item == 'self.loop':
                continue

            if item.find('.') < 0:
                continue

            target, register = item.split('.')

            if target not in related_device_map:
                related_device_map[target] = dict(register=list(), function=list())

            if register not in related_device_map[target]['register']:
                related_device_map[target]['register'].append(register)

        self.related_device_map = related_device_map

        self.active_record_stack = list()

    @staticmethod
    def cmp_gt(a, b):
        return a > b

    @staticmethod
    def cmp_ge(a, b):
        return a >= b

    @staticmethod
    def cmp_lt(a, b):
        return a < b

    @staticmethod
    def cmp_le(a, b):
        return a <= b

    @staticmethod
    def cmp_eq(a, b):
        return a == b

    @staticmethod
    def cmp_ne(a, b):
        return a != b

    @staticmethod
    def cmp_and(a, b):
        return a and b

    @staticmethod
    def cmp_or(a, b):
        return a or b

    def switch_in(self):
        """流程切换为执行状态"""
        print("switch in", self.name)
        for ins in self.inset_in:
            ins.reset()
            ins.execute(self)

        for ins in self.inset_running:
            ins.reset()
            ins.execute(self)

        now = time.time()
        self.last_active_timestamp = now
        self.active_record_stack.append({'switch-in': now})

    def calc(self, a, env):
        if isinstance(a, float) or isinstance(a, int):
            v_a = a
        elif a == 'self.loop':
            v_a = len(self.active_record_stack) - 1
        else:
            target, register = a
            v_a = env[target][register]
        return v_a

    def process_running_instruction(self):
        for ins in self.inset_running:
            ins.execute(self)

    def inspection(self, env):
        """
        测试判断条件真假
        返回：
            下一个要执行的流程单元, reason
        """
        if self.timeout == 0:
            next_flow = self.true_flow
            self.last_inspection_result = "timeout == 0 (流程要求立即超时)"
        elif self.timeout > 0 and time.time() - self.last_active_timestamp >= self.timeout:
            next_flow = self.true_flow
            self.last_inspection_result = "timeout == {} (超时)".format(self.timeout)
        elif len(self.conditions) == 3:
            # a > b style
            a, cmp, b = self.logic_conditions
            v_a = self.calc(a, env)
            v_b = self.calc(b, env)

            result = cmp(v_a, v_b)

            self.last_inspection_result = "[{}({}) {} {}({})] == {}".\
                format(self.conditions[0], v_a,  self.conditions[1], self.conditions[2], v_b, result)

            if result is True:
                next_flow = self.true_flow
            else:
                next_flow = self.false_flow
        elif len(self.conditions) == 7:
            # a > b && c < d style
            a, cmp1, b, logic, c, cmp2, d = self.logic_conditions
            v_a = self.calc(a, env)
            v_b = self.calc(b, env)
            v_c = self.calc(c, env)
            v_d = self.calc(d, env)

            result1 = cmp1(v_a, v_b)
            reason1 = "[{}({}) {} {}({})] == {}".\
                format(self.conditions[0], v_a,  self.conditions[1], self.conditions[2], v_b, result1)

            result2 = cmp2(v_c, v_d)
            reason2 = "[{}({}) {} {}({})] == {}".\
                format(self.conditions[4], v_c,  self.conditions[5], self.conditions[6], v_d, result2)

            result = logic(result1, result2)

            self.last_inspection_result = "[[{}] {} [{}]] == {}".format(reason1, self.conditions[3], reason2, result)

            if result is True:
                next_flow = self.true_flow
            else:
                next_flow = self.false_flow
        else:
            next_flow = self.false_flow
            self.last_inspection_result = "永远不超时"

        self.last_target_flow = next_flow
        return next_flow

    def switch_out(self):
        """流程退出执行状态"""
        for ins in self.inset_out:
            ins.reset()
            ins.execute(self)

        self.active_record_stack[-1]['switch-out'] = time.time()
        self.active_record_stack[-1]['this'] = self
        self.active_record_stack[-1]['reason'] = self.last_inspection_result
        self.active_record_stack[-1]['next'] = self.last_target_flow

        return self.last_inspection_result


class FlowsObject:
    """流程对象"""
    def __init__(self, source, net):
        self.source = source
        self.flows_net = net

        self.active_flow = None

    def run(self):
        if self.active_flow is None:
            entry_name_list = self.source.get_flow_name_list()
            entry_flow_name = entry_name_list[0]
            self.active_flow = self.flows_net[entry_flow_name]
            self.active_flow.switch_in()

        env = dict()
        for dev_type in self.active_flow.related_device_map:
            status, registers, reason = api.device_get_yc(dev_type)
            env[dev_type] = registers

        next_flow = self.active_flow.inspection(env)
        if next_flow != self.active_flow:
            reason = self.active_flow.switch_out()
            print(reason)

            if next_flow:
                next_flow.switch_in()
            self.active_flow = next_flow
        else:
            self.active_flow.process_running_instruction()

        if self.active_flow:
            return True
        else:
            return False

    def is_device_supported(self, dev_type, vendor, model, version):
        """测试指定的设备是否受到支持"""
        try:
            return version in self.source['require'][dev_type][vendor][model]
        except KeyError:
            return False

    def _link(self, dev_type):
        """
        尝试将系统中的设备链接进来
        :return:
            成功 'ok', self, 'no error'
            失败 'error', None, reason
        """
        status, dev, fail_reason = api.device_get_profile(dev_type)

        if status != api.OK:
            return api.return_warning_payload(fail_reason)

        if dev is None:
            return api.return_warning_payload("类型<{}>对应的设备驱动可能还没有启动！".format(dev_type))

        try:
            vendor = dev['vendor']
            model = dev['model']
            version = dev['version']
        except KeyError:
            return api.return_warning_payload("类型<{}>对应的设备驱动参数内容错误！".format(dev_type))

        supported = self.is_device_supported(dev_type, vendor, model, version)
        if not supported:
            return api.return_warning_payload("类型<{}/{}/{}/{}>对应的设备驱动不受支持！".
                                              format(dev_type, vendor, model, version))
        else:
            return api.return_ok_payload(self)

    def link(self):
        return api.return_ok_payload(None)


class FlowSource:
    """流程源文件对象"""
    def __init__(self, src, flow_name, full_path):
        self.src = src
        self.flow_name = flow_name
        self.full_path = full_path

        stat = os.stat(full_path)
        file_create_time = time.localtime(stat.st_ctime)
        self.file_create_time = time.strftime(profile.DT_FORMAT, file_create_time)

        file_modify_time = time.localtime(stat.st_mtime)
        self.file_modify_time = time.strftime(profile.DT_FORMAT, file_modify_time)

        self.source_status = {
            "流程来源": self.flow_name,
            "流程解析路径": self.full_path,
            "流程文件创建时间": self.file_create_time,
            "流程文件最后修改时间": self.file_modify_time,
            "流程数量": len(self),
            "流程入口": self.get_flow_name_list()[0],
            "入口列表": json.dumps(self.get_flow_name_list(), ensure_ascii=False),
            "依赖的设备参数": self.src['require']
        }

    def get_status_map(self):
        return self.source_status

    def get_relate_path(self):
        """获取流程文件的相对路径"""
        return self.full_path[len(profile.platform_root_dir)+1:]

    def get_absolute_path(self):
        """获取流程文件的绝对路径"""
        return self.full_path

    def get_flow_name(self):
        """获取流程文件的名称"""
        return self.flow_name

    def __len__(self):
        """默认用于测算流程文件中的流程数量"""
        try:
            return len(self.get_flow_name_list())
        except KeyError:
            return 0

    def get_flow_counter(self):
        """默认用于测算流程文件中的流程数量"""
        return len(self)

    def get_flow_name_list(self):
        """获取流程名列表"""
        try:
            r = re.compile(r'[^\d]+(?P<o>\d+)')

            def name_key(k):
                rk = r.match(k)
                return int(rk.groupdict()['o'])
            return sorted(self.src['flows'].keys(), key=name_key)
        except KeyError:
            return list()

    def get_required_device_type_list(self):
        """获取依赖的设备类型列表"""
        try:
            return self.src['require'].keys()
        except KeyError:
            return list()

    def get_require_device_type_count(self):
        """获取依赖的设备类型数量"""
        return len(self.get_required_device_type_list())

    def compile_flow_as_object(self, name, next_name):
        """
        将字典对象编译为FlowUnitObject
        这一步里面将true_flow, false_flow编译为流程名
        """
        f = self.src['flows'][name]

        if len(f) == 0:
            reason = "流程<{}>是空内容.".format(name)
            return api.return_warning_payload(reason)

        try:
            inset_in = [Instruction(stage='switch-in', **ins) for ins in f['inset_in']]
        except KeyError:
            inset_in = list()

        try:
            inset_running = [Instruction(stage='running', **ins) for ins in f['inset_running']]
        except KeyError:
            inset_running = list()

        try:
            inset_out = [Instruction(stage='switch-out', **ins) for ins in f['inset_out']]
        except KeyError:
            inset_out = list()

        try:
            conditions = f['conditions']
        except KeyError:
            conditions = list()

        try:
            timeout = f['timeout']
        except KeyError:
            timeout = -1

        auto_name = '$auto'
        try:
            true_flow = f['true']
        except KeyError:
            true_flow = next_name

        if true_flow == auto_name:
            true_flow = next_name

        try:
            false_flow = f['false']
        except KeyError:
            false_flow = name

        if false_flow == auto_name:
            false_flow = name

        flow_names_list = self.get_flow_name_list()
        if true_flow and true_flow not in flow_names_list:
            reason = "流程<{}>的true分支地址<{}>不可达.".format(name, true_flow)
            return api.return_warning_payload(reason)

        if true_flow and false_flow not in flow_names_list:
            reason = "流程<{}>的false分支地址<{}>不可达.".format(name, false_flow)
            return api.return_warning_payload(reason)

        flow_unit = FlowUnitObject(name, inset_in, inset_running, inset_out, conditions, timeout, true_flow, false_flow)
        return api.return_ok_payload(flow_unit)

    def compile(self):
        """
        将流程源文件编译成流程对象
        这里是获取流程对象的唯一接口
        :return:
            成功 'ok', FlowsObject, 'no error'
            失败 'error', None, reason
        """
        # 1. 最基本要求是需要有流程单元
        if not len(self):
            fail_reason = "流程文件没有具体有效的流程单元!"
            return api.return_error_payload(fail_reason)

        # 2. 链接流程单元
        fail_reason_set = list()

        a_list = self.get_flow_name_list()
        b_list = a_list[::]
        b_list.pop(0)
        b_list.extend([None])

        flow_route_net = dict()
        for this_name, next_name in zip(a_list, b_list):
            status, flow_unit, reason = self.compile_flow_as_object(this_name, next_name)
            if status != api.OK:
                fail_reason_set.append(reason)
            else:
                flow_route_net[this_name] = flow_unit

        if len(fail_reason_set):
            return api.return_error_payload(fail_reason_set)

        # build the reference net.
        for name in flow_route_net.keys():
            true_name = flow_route_net[name].true_flow
            false_name = flow_route_net[name].false_flow

            if true_name:
                flow_route_net[name].true_flow = flow_route_net[true_name]

            if false_name:
                flow_route_net[name].false_flow = flow_route_net[false_name]

        flow_object = FlowsObject(self, flow_route_net)
        return api.return_ok_payload(flow_object)


class FlowLoader:
    """流程文件加载器"""
    def load(self, flow_name, prj_id=None):
        """
        加载流程源文件
        尝试从平台流程数据库和项目数据库中加载流程文件，优先加载项目目录中的流程文件
        :param flow_name: 流程名
        :param prj_id: 项目ID
        :return:
            成功 'ok', FlowSourceObject, 'no error'
            失败 'error', None, reason
        """
        fail_reason_stack = list()

        if prj_id:
            status, project_flow_source, reason = self._try_load_from_project_flow_database(prj_id, flow_name)
            if status != api.OK:
                fail_reason_stack.append(reason)

            if project_flow_source:
                return api.return_ok_payload(project_flow_source)

        status, platform_flow_source, reason = self._try_load_from_platform_flow_database(flow_name)
        if status != api.OK:
            fail_reason_stack.append(reason)

        if platform_flow_source:
            return api.return_ok_payload(platform_flow_source)

        fail_reason_set = '\n'.join([str(reason) for reason in fail_reason_stack])
        return api.return_error_payload(fail_reason_set)

    @staticmethod
    def load_source_from_abs_path(flow_name, full_file_path):
        """加载指定的文件"""
        if not os.path.exists(full_file_path):
            return api.return_warning_payload("流程文件{}({})没有找到！".format(flow_name, full_file_path))

        try:
            flow_as_dict_source = flowfile.FlowFileReader(full_file_path).as_dict()
        except (xlrd.XLRDError, xlrd.XLDateError):
            return api.return_error_payload("文件格式不符或内容错误!")

        source = FlowSource(flow_as_dict_source, flow_name, full_file_path)
        return api.return_ok_payload(source)

    def _try_load_from_platform_flow_database(self, flow_name):
        """
        尝试从平台的流程数据库中加载源文件
        Note. 失败时不认为是错误
        :return:
            成功: 'ok', FlowSourceObject, 'no error'
            失败 'error', None, reason
        """
        full_path = '/'.join([profile.platform_profile_dir, 'flows', flow_name])
        return self.load_source_from_abs_path(flow_name, full_path)

    def _try_load_from_project_flow_database(self, prj_id, flow_name):
        """
        尝试从项目的流程数据库中加载源文件
        Note. 失败不认为是错误
        :return:
            成功: FlowSourceObject
            失败: None
        """
        project_storage_node = profile.get_project_storage_node(prj_id)
        full_path = '/'.join([profile.project_documents_dir, project_storage_node, 'flows', flow_name])
        return self.load_source_from_abs_path(flow_name, full_path)


if __name__ == '__main__':
    _, source_object, _ = FlowLoader().load('test.xlsx')
    _status, _flow_object, _reason = source_object.compile()
    _flow_object.link()
    print(_status, _flow_object, _reason)

    live = True
    while live:
        last = time.time()
        live = _flow_object.run()
        delta = time.time() - last
        print("spent", delta * 1000, 'ms')
        time.sleep(1)
