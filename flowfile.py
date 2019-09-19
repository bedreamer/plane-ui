# -*- coding: utf-8 -*-
import re
import xlsxwriter
import xlrd


class FlowFileReader:
    """流程文件读取对象"""
    def __init__(self, full_path):
        self.full_path = full_path
        self.workbook = xlrd.open_workbook(self.full_path)

    @staticmethod
    def get_require(sheet):
        if sheet is None:
            return dict()

        require = dict()
        for idx, columns in enumerate(sheet.get_rows()):
            if idx == 0:
                continue

            _ = columns[0].value
            code = columns[1].value
            vendor = columns[2].value
            model = columns[3].value
            version = columns[4].value

            if code not in require:
                require[code] = dict()

            if vendor not in require[code]:
                require[code][vendor] = dict()

            if model not in require[code][vendor]:
                require[code][vendor][model] = list()

            require[code][vendor][model].extend([version])

        return require

    @staticmethod
    def get_flow(sheet):
        step = dict()

        name_cell = sheet.cell_value(1, 1)
        step['timeout'] = int(sheet.cell_value(1, 3))
        conditions = str(sheet.cell_value(2, 1)).lstrip().rstrip()
        step['true'] = str(sheet.cell_value(3, 1)).lstrip().rstrip()
        step['false'] = str(sheet.cell_value(3, 3)).lstrip().rstrip()

        if len(conditions) == 0:
            step['conditions'] = list()
        else:
            ops_list = ['>=', '>', '<=', '<', '!=', '==', '&&', '||']
            for op in ops_list:
                if conditions.find(op) >= 0:
                    conditions = conditions.replace(op, op.join([',', ',']))

            conditions = re.sub(r'\s+', '', conditions, flags=re.UNICODE)
            if ',' in conditions:
                conditions_list = conditions.split(',')
            else:
                conditions_list = [conditions]

            for idx, s in enumerate(conditions_list[::]):
                try:
                    v = int(s)
                    conditions_list[idx] = v
                except ValueError:
                    try:
                        v = float(s)
                        conditions_list[idx] = v
                    except ValueError:
                        pass

            step['conditions'] = conditions_list

        switch_in_operations = list()
        running_operations = list()
        switch_out_operations = list()

        offset = 0
        while True:
            try:
                stage = str(sheet.cell_value(7 + offset, 0)).lstrip().rstrip()
                if stage == '':
                    raise IndexError
                period = int(sheet.cell_value(7 + offset, 1))
                function = str(sheet.cell_value(7 + offset, 2)).lstrip().rstrip()
                args = str(sheet.cell_value(7 + offset, 3)).lstrip().rstrip()
            except (IndexError, ValueError):
                break

            if '' in [stage, period, function]:
                break

            target, function = function.split('.')
            operation = {
                'period': period,
                'target': target,
                'function': function,
            }
            if len(args):
                operation['args'] = args.split(',')
            else:
                operation['args'] = list()

            if stage == '进入':
                switch_in_operations.append(operation)
            elif stage == '执行':
                running_operations.append(operation)
            elif stage == '退出':
                switch_out_operations.append(operation)
            else:
                break
            offset += 1

        if len(switch_in_operations):
            step['inset_in'] = switch_in_operations
        if len(running_operations):
            step['inset_running'] = running_operations
        if len(switch_out_operations):
            step['inset_out'] = switch_out_operations

        return dict({name_cell: step})

    def as_dict(self):
        source = dict()

        # 处理设备依赖关系
        try:
            sheet = self.workbook.sheet_by_name('设备依赖')
            require = self.get_require(sheet)
            source.update(require=require)
        except ValueError:
            pass

        # 处理流程定义页面
        r = re.compile(r's(?P<o>\d+)')
        flows = dict()
        for sheet in self.workbook.sheets():
            if r.match(sheet.name) is None:
                continue
            _flow = self.get_flow(sheet)
            flows.update(**_flow)

        if len(flows):
            source['flows'] = flows

        return source


class FlowFileWriter:
    """流程文件写入对象"""
    def __init__(self, full_path):
        self.full_path = full_path
        self.workbook = xlsxwriter.Workbook(full_path)

    def get_worksheet(self, name):
        """
        返回工作表
        :param name: 工作表名
        :return:
            存在，返回Worksheet，
            不存在，返回None
        """
        return self.workbook.get_worksheet_by_name(name)

    def add_worksheet(self, name):
        """
        添加工作表
        :param name: 工作表名
        :return:
            返回Worksheet，
        """
        worksheet = self.get_worksheet(name)
        return worksheet if worksheet is not None else self.workbook.add_worksheet(name)

    def get_worksheets_name_list(self):
        """
        获取工作表名
        :return: list()
        """
        return [sheet.name for sheet in self.workbook.worksheets()]

    def create_template_for_device(self, device_list):
        """
        根据项目需求保存一份流程文件模板
        :param device_list: 设备列表
        """

        title_format = self.workbook.add_format({
            'align': 'center',
            'bold': True,
            'fg_color': '#a0c5e8',
        })
        head_format = self.workbook.add_format({
            'align': 'center',
            'bold': True,
            'bg_color': '#DDDDDD'
        })
        body_format = self.workbook.add_format({
            'align': 'center',
        })

        fill_notice = """填写说明：
        1. 这个文件是自动生成的，请按照既定的规则进行填写。
        2. 填写完成后务必回传至软件进行有效性校验。
        3. 如果是从软件导出的模板，请勿更改<设备依赖>表格。
        4. 如果是手动添加的流程文件，请手动添加<设备依赖>表格确保流程能被软件识别接受。
        5. 对于来自软件的模板文件，会存在一张模板步骤表<s1>，这张表将作为流程的入口步骤执行。
        6. 对于新增步骤的需求建议复制表格<s1>，然后在新的表格里进行修改。
        7. 编辑过程中请勿随意修改表格格式。
        """

        # 填写说明
        sheet = self.add_worksheet('填写说明')
        sheet.set_column('A:A', 160)
        for line, txt in enumerate(fill_notice.split('\n')):
            sheet.write('A{}'.format(line + 1), txt)

        # 设备需求配置页面
        sheet = self.add_worksheet('设备依赖')
        sheet.set_column('A:E', 20)

        titles = ['设备类型', '代码', '生产商', '型号', '版本']
        columns = ['A', 'B', 'C', 'D', 'E']
        for pos, title in zip(columns, titles):
            sheet.write(''.join([pos, '1']), title, title_format)

        for idx, device in enumerate(device_list):
            context = [device.type.name, device.type.code, device.vendor, device.model, device.version]
            for pos, txt in zip(columns, context):
                sheet.write(''.join([pos, str(idx+2)]), txt, body_format)

        # 添加一个流程模板页面
        sheet_name = 's1'
        sheet = self.add_worksheet(sheet_name)
        sheet.set_column('A:B', width=14, cell_format=body_format)
        sheet.set_column('C:D', width=20, cell_format=body_format)
        sheet.set_column('E:E', width=2)
        sheet.set_column('F:I', width=20)

        sheet.merge_range('A1:D1', '流程摘要', title_format)
        sheet.merge_range('A6:D6', '指令集合', title_format)

        sheet.write('F1', '支持的函数', title_format)
        sheet.write('G1', '函数参数范围', title_format)

        sheet.write('H1', '支持的寄存器', title_format)
        sheet.write('I1', '寄存器范围', title_format)

        sheet.write('A2', '步骤名', head_format)
        sheet.write('B2', sheet_name, body_format)
        sheet.data_validation('B2', {
            'validate': 'length',
            'criteria': '>',
            'value': 0,
            'input_title': '输入流程步骤名:',
            'input_message': '流程步骤名必须和表格名称相同.\n'
                             '例如：s1, s2, s3....，否则认为这个步骤为无效状态。',
            'error_title': '需要流程名!',
            'error_message': '必须设定这个流程名'
        })

        sheet.write('C2', '最大执行时长(秒)', head_format)
        sheet.write('D2', '-1', body_format)
        sheet.data_validation('D2', {
            'validate': 'integer',
            'criteria': '>=',
            'value': -1,
            'input_title': '输入流程最大执行时间:\n',
            'input_message': '-1表示用不超时\n'
                             '0表示不执行判定条件，执行完指令后立即结束\n'
                             '其他时间表示这个步骤的最大执行时间',
            'error_title': '错误!',
            'error_message': '需要设置步骤最大执行时间'
        })

        sheet.write('A3', '判定条件', head_format)
        sheet.write('B3', '', body_format)
        sheet.data_validation('B3', {
            'validate': 'length',
            'criteria': '>=',
            'value': 0,
            'input_title': '输入判定条件:',
            'input_message': '比较关系: >, >=, <, <=, ==, !=, &&, ||',
            'error_title': '错误!',
            'error_message': '输入正确的判定条件'
        })

        sheet.merge_range('B3:D3', '', body_format)
        sheet.write('A4', '成功跳转', head_format)
        sheet.write('B4', '$auto', body_format)
        sheet.data_validation('B4', {
            'validate': 'length',
            'criteria': '>',
            'value': 0,
            'input_title': '输入跳转步骤名:',
            'input_message': '判定条件成立的情况下，'
                             '下一步要执行的步骤名，$auto表示自动切换至以步骤名排序的下一步。',
            'error_title': '错误!',
            'error_message': '输入正确的步骤名'
        })

        sheet.write('C4', '失败跳转', head_format)
        sheet.write('D4', '$auto', body_format)
        sheet.data_validation('D4', {
            'validate': 'length',
            'criteria': '>',
            'value': 0,
            'input_title': '输入跳转步骤名:',
            'input_message': '判定条件不成立的情况下，'
                             '下一步要执行的步骤名，$auto表示继续指定当前步骤。',
            'error_title': '错误!',
            'error_message': '输入正确的步骤名'
        })

        ins_set_head = ['指令阶段', '周期(秒)', '函数', '参数(用,分隔多个参数)']
        columns = ['A7', 'B7', 'C7', 'D7']
        for pos, head in zip(columns, ins_set_head):
            sheet.write(pos, head, head_format)

        # 指令阶段有效性
        ins_stage_set = ['进入', '执行', '退出']
        sheet.data_validation('A8:A100', {
            'validate': 'list',
            'source': ins_stage_set,
            'input_title': '选择一个指令阶段:',
            'input_message': '进入：刚准备执行这条指令前的阶段，用于执行一些初始化动作\n'
                             '执行：指令处于正常执行阶段\n'
                             '退出：指令执行完毕，用于执行一些收尾动作',
        })

        # 设置周期有效性
        sheet.data_validation('B8:B100', {
            'validate': 'integer',
            'criteria': '>=',
            'value': 0,
            'input_title': '输入一个整数:',
            'input_message': '数据需要大于等于0，0表示只执行一次',
            'error_title': '周期参数错误!',
            'error_message': '数据范围必须大于等于0'
        })

        # 函数以及函数有效性
        supported_functions_list = list()
        supported_registers_list = list()
        for device in device_list:
            code = device.type.code

            funs_list = device.get_supported_function_list()
            supported_functions_list.extend([[code, name, function] for name, function in funs_list.items()])

            regs_list = device.get_supported_registers_list()
            supported_registers_list.extend([[code, name, register] for name, register in regs_list.items()])

        for idx, ll in enumerate(supported_functions_list):
            code, name, function = ll
            txt = '.'.join([code, name])
            sheet.write(''.join(['F', str(idx+2)]), txt)
            sheet.write(''.join(['G', str(idx+2)]), function['valid_string'], body_format)

        sheet.write('H2', 'self.loop')
        sheet.write('I2', '>= 0', body_format)
        for idx, ll in enumerate(supported_registers_list):
            code, name, register = ll
            txt = '.'.join([code, name])
            sheet.write(''.join(['H', str(idx+3)]), txt)
            sheet.write(''.join(['I', str(idx+3)]), register['valid_string'], body_format)

        # 设置函数的有效性数据， 总是比F列实际数据多10个
        function_select_range = '=$F$2:$F${}'.format(len(supported_functions_list) + 12)
        sheet.data_validation('C8:C100', {
            'validate': 'list',
            'source': function_select_range,
            'input_title': '选择一个具体的函数:',
            'input_message': '选择一个合适的函数来实现具体的业务。'
                             '如果没有找到合适的函数，你需要确认是否选择了正确的设备'
        })

        # 设置函数参数输入提示
        sheet.data_validation('D8:D100', {
            'validate': 'length',
            'criteria': '>=',
            'value': 0,
            'input_title': '输入函数的参数:',
            'input_message': '需要注意的是：这里的参数范围需要手动确认是否有效，'
                             '具体的做法是参考·支持的函数列内具体的参数范围定义·'
        })

    def save(self):
        """
        保存一个新的流程文件
        """
        self.workbook.close()


if __name__ == '__main__':
    import json

    # from storage.models import *
    # flow = FlowFileWriter('test.xlsx')
    # devices_list = PlaneDevice.objects.all()
    # flow.create_template_for_device(devices_list)
    # flow.save()

    flow = FlowFileReader('test.xlsx')
    print(json.dumps(flow.as_dict(), indent=4, ensure_ascii=False))
