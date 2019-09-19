# -*- coding: utf-8 -*-
from django.db import models
import django.utils.timezone as timezone
import sys
import os
import importlib
import zipimport
import shutil
import profile
import pytz
import datetime


# 服务记录
_service_pack = None


class ServiceRecord(models.Model):
    """服务记录"""
    key = models.CharField(max_length=100, default='', help_text='键名')
    value = models.TextField(default='', help_text='值')

    @classmethod
    def as_dict(cls):
        global _service_pack

        if not _service_pack:
            _service_pack = {r.key: r.value for r in cls.objects.all()}

        return _service_pack


class PlaneDeviceType(models.Model):
    """支持的设备类型"""
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100, help_text="设备类型名")
    description = models.TextField(help_text="设备类型描述")


class PlaneDevice(models.Model):
    """设备抽象对象"""
    type = models.ForeignKey(PlaneDeviceType, on_delete=models.CASCADE, help_text="设备代码")

    vendor = models.CharField(max_length=100, help_text="厂家名称")
    model = models.CharField(max_length=100, help_text="设备型号")
    version = models.CharField(max_length=100, help_text="设备版本号")

    conf = models.TextField(help_text="设备驱动配置文件")
    driver = models.CharField(max_length=100, help_text="驱动文件名")

    create_datetime = models.DateTimeField(default=timezone.now, help_text="设备驱动创建时间")

    ps_uuid = models.CharField(max_length=100, default='', help_text="驱动定位/进程定位")

    def get_driver_module(self):
        """根据self.driver提示获驱动模块"""

        if self.driver[::-1].find(profile.DRV_FILE_SUFFIX[::-1]) == 0:
            path = '/'.join([profile.platform_device_drivers_dir, self.driver])
            zip_module = zipimport.zipimporter(path)
            return zip_module.load_module('driver')
        else:
            return importlib.import_module('.'.join(['drivers', self.driver]))

    def get_supported_function_list(self):
        module = self.get_driver_module()
        return module.Information.get_functions_list()

    def get_supported_registers_list(self):
        module = self.get_driver_module()
        return module.Information.data_register_list()

    def dump(self):
        """显示驱动详细信息"""
        print("ID：", self.id)
        print("=" * 40)
        print("UUID:", self.ps_uuid)
        print("注册时间：", self.create_datetime)
        print("类型名：", self.type.name)
        print("类型代码：", self.type.code)
        print("生产商：", self.vendor)
        print("型号：", self.model)
        print("版本号：", self.version)
        print("驱动配置文件：", self.conf)
        print("驱动：", self.driver)
        print()


class PlaneDefaultDevice(models.Model):
    """默认设备配置表"""
    type = models.ForeignKey(PlaneDeviceType, on_delete=models.CASCADE, help_text="设备代码")
    device = models.ForeignKey(PlaneDevice, on_delete=models.CASCADE, help_text="设备")
    update_datetime = models.DateTimeField(default=timezone.now, help_text="设置为默认设备的日期时间")

    @classmethod
    def get_default(cls, dev_type):
        try:
            dtype = PlaneDeviceType.objects.get(code=dev_type)
        except PlaneDeviceType.DoesNotExist:
            return None

        try:
            default = PlaneDefaultDevice.objects.get(type=dtype)
        except PlaneDefaultDevice.DoesNotExist:
            return None

        return default.device

    @classmethod
    def set_default(cls, dev_id):
        try:
            device = PlaneDevice.objects.get(id=dev_id)
        except PlaneDevice.DoesNotExist:
            return None

        try:
            default = PlaneDefaultDevice.objects.get(type=device.type)
        except PlaneDefaultDevice.DoesNotExist:
            default = PlaneDefaultDevice(type=device.type)

        default.device = device
        default.update_datetime = timezone.now()
        default.save()

        return device


class PlaneDeviceHistory(models.Model):
    """驱动文件操作历史"""
    operation = models.CharField(max_length=100, help_text="操作说明")
    operation_datetime = models.DateTimeField(default=timezone.now, help_text="操作时间")
    origin_path = models.TextField(help_text="原始文件路径")
    target_path = models.TextField(help_text="最终文件路径")


# Create your models here.
class Project(models.Model):
    """测试项目抽象对象"""
    name = models.CharField(max_length=40, default="<项目名称>", help_text="项目名称")
    sn = models.CharField(max_length=40, default="无", help_text="项目编号， 由实验室决定是否使用")
    subscript = models.TextField(default="<项目摘要>", help_text="项目摘要")
    description = models.TextField(default="<项目介绍>", help_text="项目介绍")
    create_datetime = models.DateTimeField(default=timezone.now, help_text="项目创建时间")
    status = models.CharField(default='初始化', max_length=100, help_text="项目当前状态")

    def start_services(self):
        """启动项目的依赖服务"""
        if self.status != profile.PRJ_STATUS_RUNNING:
            return

    def stop_service(self):
        """启动项目的依赖服务"""
        if self.status != profile.PRJ_STATUS_RUNNING:
            return

    def get_dict_format(self):
        """进行JSON格式化"""
        return {
            'id': self.id,
            'name': self.name,
            'subscript': self.subscript,
            'description': self.description,
            'create_datetime': str(self.create_datetime),
            'status': self.status,
        }

    def get_storage_node(self):
        """获取存储名"""
        return profile.get_project_storage_node(self.id)

    @staticmethod
    def storage_node_to_id(node):
        """将存储名转换为ID"""
        return int(node[4:])

    def get_storage_root(self):
        """获取存储位置的根目录路径"""
        node = self.get_storage_node()
        return '/'.join([profile.project_documents_dir, node])

    def get_flow_storage_root(self):
        """获取流程文件存储目录"""
        return '/'.join([self.get_storage_root(), 'flows'])

    def init_storage_directory(self):
        """初始化存储目录"""
        prj_root = self.get_storage_root()

        os.mkdir(prj_root, profile.default_dir_mode)
        sub_directory = ['data', 'log', 'flows', 'scripts']
        for sub_dir in sub_directory:
            path = '/'.join([prj_root, sub_dir])
            os.mkdir(path)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        need_init_storage = False

        if self.id is None:
            need_init_storage = True
        super().save(force_insert, force_update, using, update_fields)

        if need_init_storage:
            self.init_storage_directory()

    def get_status_detail(self):
        """
            获取项目的最新状态
            返回：
                成功：ProjectStateLog
                失败：None
        """
        change_log = ProjectStateLog.objects.filter(project=self).order_by('-change_datetime')
        if len(change_log) == 0:
            return None
        else:
            return change_log[0]

    def set_status(self, status, comment):
        """
        设置新的状态
        :param status: 状态名
        :param comment: 设置状态时的备注
        :return:
        """
        if status == self.status:
            return status

        log = ProjectStateLog(project=self, old_status=self.status, new_status=status, comment=comment)

        self.status = status
        self.save()

        log.save()
        return status

    def get_depended_device_list(self):
        """
        获取相关关联的设备列表
        :return:
            成功：Device list
        """
        return [bind.device for bind in ProjectWithDevice.objects.filter(project=self)]

    def get_depended_device_type_list(self):
        """
        获取项目依赖的设备类型
        :return:
            PlaneDeviceType list
        """
        return [device.type for device in self.get_depended_device_list()]


class ProjectStateLog(models.Model):
    """项目状态切换日志"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text="项目")
    old_status = models.CharField(max_length=100, default='', help_text='旧的项目状态')
    new_status = models.CharField(max_length=100, default='', help_text="新的项目状态")
    change_datetime = models.DateTimeField(default=timezone.now, help_text="切换时间")
    comment = models.TextField(default='', help_text="状态切换的备注")


class ProjectWithDevice(models.Model):
    """项目和设备的关联表"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text="项目")
    device = models.ForeignKey(PlaneDevice, on_delete=models.CASCADE, help_text="设备")


class FlowFile(models.Model):
    """流程文件"""
    version = models.CharField(max_length=100, default='v1.0', help_text="流程文件版本")
    origin_path = models.TextField(default='', help_text="原始流程文件路径")
    name = models.CharField(max_length=100, default='', help_text="流程文件名")
    create_datetime = models.DateTimeField(default=timezone.now, help_text="流程创建时间")
    update_datetime = models.DateTimeField(default=timezone.now, help_text="流程更新时间")

    def clone_flow_file_from_path(self, temp_flow_file_path):
        """从临时文件处克隆流程文件"""
        version = FlowFileHistory(flow=self)
        version.save()

        shutil.copy(temp_flow_file_path, version.get_storage_path())
        return self

    def get_flow_file_as_abs_path(self):
        """获取流程文件的完整路径"""
        try:
            version = FlowFileHistory.objects.filter(flow=self).order_by('id').last()
            return version.get_storage_path()
        except FlowFileHistory.DoesNotExist:
            return None


class FlowFileHistory(models.Model):
    """流程文件不同版本"""
    flow = models.ForeignKey(FlowFile, on_delete=models.CASCADE)
    update_datetime = models.DateTimeField(default=timezone.now, help_text="流程更新时间")

    def get_storage_name(self):
        """
        获取存储文件名, 名字取成zip格式为了混淆数据，让用户依赖软件
        """
        return '{:08d}-{:08d}{}'.format(self.flow.id, self.id, profile.FLOW_FILE_SUFFIX)

    def get_storage_path(self):
        """获取流程文件存储目录"""
        return '/'.join([profile.flowfile_storage_dir, self.get_storage_name()])


class ProjectWithFlow(models.Model):
    """项目和流程文件的关联表"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text="关联的项目")
    flow = models.ForeignKey(FlowFile, on_delete=models.CASCADE, help_text="关联的流程文件")
    active = models.BooleanField(default=False, help_text='流程是否处于激活/执行状态')
    comment = models.TextField(default='', help_text="对这个流程的备注说明")
    bind_datetime = models.DateTimeField(default=timezone.now, help_text="绑定时间")


class Message(models.Model):
    """发布消息"""
    type = models.CharField(default='info', max_length=100, help_text="消息类型，info/warn/error")
    create_datetime = models.DateTimeField(default=timezone.now, help_text="消息更新时间")
    expire_datetime = models.DateTimeField(default=datetime.datetime(2019, 12, 31, 23, 59, 59, 999, tzinfo=pytz.UTC), help_text="过期时间")
    show_count = models.IntegerField(default=1, help_text="最大显示次数")

    title = models.CharField(max_length=100, default='消息', help_text='消息标题')
    txt = models.TextField(default='', help_text='消息主体内容')
    ref_href = models.TextField(default='', help_text="参考链接")
    ref_title = models.CharField(max_length=100, default='参考', help_text='参考链接标题')
    ref_target = models.CharField(max_length=100, default='_self', help_text='参考链接打开方式， _blank, _self')
