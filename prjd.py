# -*- coding: utf-8 -*-
# author: lijie
import profile
from storage.models import *
import os
import time
import uuid
import api


def load_project():
    """加载项目"""
    status, prj, reason = api.project_get_current()
    if status != api.OK:
        print(reason)
        return

    status, prj, reason = api.project_services_start(prj.id)
    if status != api.OK:
        print(reason)
        return


def list_all_project():
    """显示项目列表"""
    for prj in Project.objects.all():
        print("{}        {}      {}".format(prj.id, prj.name, prj.sn))


def dump_all_project(prj_id):
    """显示项目状态"""
    status, prj, reason = api.project_get(prj_id)
    if status != api.OK:
        print(reason)
        return

    print(prj.id)
    print("=" * 40)
    for field in prj._meta.fields:
        if field.attname == 'id':
            continue
        value = str(prj.__getattribute__(field.attname))
        if len(value) > 40:
            print(field.attname, ":")
            print(" " * 4, value)
        else:
            print(field.attname, ":", value)

    for bind in ProjectWithDevice.objects.filter(project=prj):
        print(bind.device.type.name, ':', bind.device.id)
        print("-" * 10)
        print("  vendor:", bind.device.vendor)
        print("  model:", bind.device.model)
        print("  version:", bind.device.version)
        print("  driver:", bind.device.driver)

    statement_change_log = ProjectStateLog.objects.filter(project=prj).order_by('-change_datetime')
    if len(statement_change_log):
        print("状态更改历史")
        print('-' * 10)

    for s in statement_change_log:
        print(str(s.change_datetime), s.old_status, '===>', s.new_status, s.comment)


def create_project(name, sn, subscript, description):
    """通过shell创建一个项目"""
    status, prj, reason = api.project_create(name, sn, subscript, description)
    if status != api.OK:
        print(reason)
        return
    print("项目创建完成, ID={}".format(prj.id))


def bind_device_with_project(prj_id, dev_id):
    """给项目绑定设备"""
    status, _, reason = api.project_register_device(prj_id, dev_id)
    if status != api.OK:
        print(reason)
        return


def unbind_device_with_project(prj_id, dev_id):
    """给项目解绑设备设备"""
    status, _, reason = api.project_unregister_device(prj_id, dev_id)
    if status != api.OK:
        print(reason)
        return


def purge_project(without_confirm):
    """清空项目记录"""
    if without_confirm is None:
        confirm = input("确定清除所有项目数据:(N/y)>").rstrip().lstrip()
        if confirm.lower() != 'y':
            return

    status, _, reason = api.purge_project()
    if status != api.OK:
        print(reason)
        return


def force_update_project_status(prj_id, status, without_confirm):
    """强制更改项目状态"""
    prj_status, project, reason = api.project_get(prj_id)
    if prj_status != api.OK:
        print(reason)
        return

    if status not in profile.PROJECT_STATUS_LIST:
        print("无法支持的状态:", status)
        return

    if status == project.status:
        return

    if without_confirm is None:
        confirm = input("确定强制更改项目状态({}==>{}):(N/y)>".format(project.status, status)).rstrip().lstrip()
        if confirm.lower() != 'y':
            return

    status, _, reason = api.project_modify_status(prj_id, status, "强制手工切换状态！")
    if status != api.OK:
        print(reason)
        return


def dump_service_status(service_status):
    for process_status in service_status:
        print('-' * 20)
        for key, value in process_status.items():
            print(key, ':', value)


def project_service_status():
    """项目服务状态"""
    status, prj, reason = api.project_get_current()
    if status != api.OK:
        print(reason)
        return

    status, service_status, reason = api.project_service_status(prj.id)
    if status != api.OK:
        print(reason)
        return

    dump_service_status(service_status)


def project_service_start():
    """启动项目服务"""
    status, prj, reason = api.project_get_current()
    if status != api.OK:
        print(reason)
        return

    status, service_status, reason = api.project_services_start(prj.id)
    if status != api.OK:
        print(reason)
        return

    dump_service_status(service_status)


def project_service_stop():
    """停止项目服务"""
    status, prj, reason = api.project_get_current()
    if status != api.OK:
        print(reason)
        return

    status, service_status, reason = api.project_service_stop(prj.id)
    if status != api.OK:
        print(reason)
        return

    dump_service_status(service_status)


def project_service_restart():
    """重启项目服务"""
    status, prj, reason = api.project_get_current()
    if status != api.OK:
        print(reason)
        return

    status, service_status, reason = api.project_service_restart(prj.id)
    if status != api.OK:
        print(reason)
        return

    dump_service_status(service_status)


if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser(usage='%prog [Command|--help] {Options}')

    group = parser.add_option_group("项目运行管理")
    group.add_option('', '--start', nargs=0, help="启动项目服务")
    group.add_option('', '--stop', nargs=0, help="停止项目服务")
    group.add_option('', '--restart', nargs=0, help="重启项目服务")
    group.add_option('', '--status', nargs=0, help="显示项目服务状态")
    group.add_option('', '--project-id', type='int', help="指定项目")

    group = parser.add_option_group("项目数据库清理")
    group.add_option('', '--purge', nargs=0, help="删除所有项目相关的数据")
    group.add_option('', '--without-confirm', nargs=0, help="不需要确认")

    group = parser.add_option_group("项目数据库管理")
    group.add_option('', '--list', nargs=0, help="显示项目列表")
    group.add_option('', '--dump', nargs=0, help="罗列项目信息")
    group.add_option('', '--create', nargs=0, help="创建项目")
    group.add_option('', '--project-name', help="项目名")
    group.add_option('', '--lab-sn', default='', help="实验室项目编号")
    group.add_option('', '--subscript', default='', help="项目摘要")
    group.add_option('', '--description', default='', help="项目描述")

    group = parser.add_option_group("项目状态管理")
    group.add_option('', '--force-set-status', type='str', help="强制更改项目状态")

    group = parser.add_option_group("项目关联设备管理")
    group.add_option('', '--bind-device', nargs=0, help="绑定设备")
    group.add_option('', '--unbind-device', nargs=0, help="设备解绑")
    group.add_option('', '--device-id', type='int', help="设备ID")
    group.add_option('', '--uuid', help="UUID")

    options, args = parser.parse_args()

    # 执行驱动服务
    if options.purge is not None:
        purge_project(options.without_confirm)
    elif options.dump is not None:
        dump_all_project(options.project_id)
    elif options.list is not None:
        list_all_project()
    elif options.force_set_status is not None:
        force_update_project_status(options.project_id, options.force_set_status, options.without_confirm)
    elif options.create is not None:
        create_project(options.project_name, options.lab_sn, options.subscript, options.description)
    elif options.bind_device is not None:
        bind_device_with_project(options.project_id, options.device_id)
    elif options.unbind_device is not None:
        unbind_device_with_project(options.project_id, options.device_id)
    elif options.status is not None:
        project_service_status()
    elif options.start is not None:
        project_service_start()
    elif options.stop is not None:
        project_service_stop()
    elif options.restart is not None:
        project_service_restart()
    else:
        pass
