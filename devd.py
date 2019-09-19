# -*- coding: utf-8 -*-
# Usage: devd.py -d dev_type -c {conf}
#
from storage.models import *
import importlib
import zipimport
import os
import shutil
import time
import api
import uuid


def get_device_driver(dev_id, conf):
    """创建设备驱动守护进程"""
    try:
        device = PlaneDevice.objects.get(id=dev_id)
    except Exception as e:
        print("无法找到id={}的设备".format(dev_id), e)
        return None

    try:
        module = device.get_driver_module()
        return module.Driver(device, conf)
    except ImportError as e:
        print(e)
        return None


def dump_device_driver_by_zipfile(zipfile_path):
    """显示设备驱动详细信息"""
    zip_module = zipimport.zipimporter(zipfile_path)
    driver = zip_module.load_module('driver')
    info = driver.Information()

    print(zipfile_path)
    print("=" * 40)
    print(info)


def dump_device_driver_by_device_id(dev_id):
    """显示设备驱动详细信息"""
    try:
        driver = PlaneDevice.objects.get(id=dev_id)
        driver.dump()
    except Exception as e:
        print(e)


def probe_device_driver_zipfile_conflict(basename):
    """
    处理zip文件名冲突， 返回新的文件名
    """
    path = '/'.join([profile.platform_device_drivers_dir, basename])

    if os.path.exists(path) is False:
        return basename

    x = basename.split(profile.DRV_FILE_SUFFIX)[0]
    tags = time.strftime(profile.DT_TIMESTAMP)

    return ''.join([x, '-', tags, profile.DRV_FILE_SUFFIX])


def update_device_driver(target_driver, zipfile_path, new_driver_module):
    """更新设备驱动"""
    old_basename = os.path.basename(zipfile_path)
    new_basename = probe_device_driver_zipfile_conflict(old_basename)
    target_zip_path = '/'.join([profile.platform_device_drivers_dir, new_basename])
    shutil.copyfile(zipfile_path, target_zip_path)

    driver_module = target_driver.get_driver_module()
    installer = driver_module.Uninstall()
    installer.uninstall()

    target_driver.driver = new_basename
    target_driver.save()

    driver_module = target_driver.get_driver_module()
    installer = driver_module.Install()
    installer.install()

    print(zipfile_path, "更新成功, ID={}, 驱动程序={}".format(target_driver.id, target_driver.driver))


def register_device_driver_by_file(zipfile_path):
    """注册设备驱动"""
    zip_module = zipimport.zipimporter(zipfile_path)
    new_driver_module = zip_module.load_module('driver')
    info = new_driver_module.Information()

    try:
        dev_type = PlaneDeviceType.objects.get(code=info.dev_type)
    except PlaneDeviceType.DoesNotExist:
        print("设备类型代码为: {}的驱动目前还未支持。".format(info.dev_type))
        return

    new_md5 = profile.calc_file_md5sum(zipfile_path)

    try:
        old_driver = PlaneDevice.objects.get(type=dev_type, vendor=info.vendor, model=info.model, version=info.version)
        old_zipfile_path = '/'.join([profile.platform_device_drivers_dir, old_driver.driver])
        old_md5 = profile.calc_file_md5sum(old_zipfile_path)

        if old_md5 == new_md5:
            print("相同的驱动已经安装过了, ID={}, 驱动程序={}".format(old_driver.id, old_driver.driver))
            return

        return update_device_driver(old_driver, zipfile_path, new_driver_module)
    except PlaneDevice.DoesNotExist:
        pass

    old_basename = os.path.basename(zipfile_path)
    new_basename = probe_device_driver_zipfile_conflict(old_basename)
    target_zip_path = '/'.join([profile.platform_device_drivers_dir, new_basename])
    shutil.copyfile(zipfile_path, target_zip_path)
    dr = PlaneDevice(type=dev_type, vendor=info.vendor, model=info.model, version=info.version,
                     driver=new_basename, ps_uuid=str(uuid.uuid1()))
    dr.save()

    try:
        driver_module = dr.get_driver_module()
        installer = driver_module.Install()
        installer.install()
        print(zipfile_path, "注册成功, ID={}, 驱动程序={}".format(dr.id, dr.driver))
    except Exception as e:
        print(zipfile_path, "注册不完全成功, ID={}, 驱动程序={}".format(dr.id, dr.driver))
        print("异常：", e)


def register_device_driver_by_module(module_name):
    """
    根据模块名注册设备驱动
    注意：这个功能只针对调试开放
    """
    print("** Warning: 这个功能只针对调试开放！")
    try:
        module = importlib.import_module('.'.join(['drivers', module_name]))
    except ImportError:
        print("没有找到名称为 {} 的模块".format(module_name))
        return

    info = module.Information()
    try:
        dev_type = PlaneDeviceType.objects.get(code=info.dev_type)
    except PlaneDeviceType.DoesNotExist:
        print("设备类型代码为: {}的驱动目前还未支持。".format(info.dev_type))
        return

    try:
        driver = PlaneDevice.objects.get(type=dev_type, vendor=info.vendor, model=info.model, version=info.version)
    except PlaneDevice.DoesNotExist:
        driver = PlaneDevice(type=dev_type, vendor=info.vendor, model=info.model, version=info.version,
                             driver=module_name, ps_uuid=str(uuid.uuid1()))

    installer = module.Install()
    installer.install()

    driver.driver = module_name
    driver.save()


def unregister_device_driver(dev_id):
    """取消注册设备驱动"""
    try:
        driver = PlaneDevice.objects.get(id=dev_id)
    except PlaneDevice.DoesNotExist:
        print("没有找ID={}的设备驱动!".format(dev_id))
        return

    dump_device_driver_by_device_id(dev_id)

    driver_module = driver.get_driver_module()
    installer = driver_module.Uninstall()
    installer.uninstall()

    driver.delete()
    print("驱动卸载成功!")


def list_all_registered_device_driver():
    """显示已经注册的设备驱动详细信息"""
    try:
        for driver in PlaneDevice.objects.all():
            driver.dump()
    except Exception as e:
        print(e)

    for driver in PlaneDefaultDevice.objects.all():
        print("{} ===> {}".format(driver.type.name, driver.device.id))


def set_device_as_default(dev_id):
    """将设备设置为默认值"""
    status, device, reason = api.device_set_default(dev_id)
    if status != api.OK:
        print(reason)


def purge_unreferenced_driver_files():
    """清理再数据库中没有被引用到的驱动文件"""
    for basename in os.listdir(profile.platform_device_drivers_dir):
        if basename[::-1].find(profile.DRV_FILE_SUFFIX[::-1]) != 0:
            continue

        drivers = PlaneDevice.objects.filter(driver=basename)
        if len(drivers) > 0:
            continue

        print("purge", basename)
        full_path = '/'.join([profile.platform_device_drivers_dir, basename])
        os.remove(full_path)


def purge_device(without_confirm):
    """清空设备相关记录"""
    if without_confirm is None:
        confirm = input("确定清除所有设备数据:(N/y)>").rstrip().lstrip()
        if confirm.lower() != 'y':
            return

    status, _, reason = api.purge_device()
    if status != api.OK:
        return


if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser(usage='%prog [Command|--help] {Options}')

    group = parser.add_option_group("驱动运行/注销")
    group.add_option('-r', '--run', nargs=0, help="运行服务")
    group.add_option('-u', '--uninstall', nargs=0, help="注销驱动")
    group.add_option('-I', '--dev-id', help="指定设备编号")
    group.add_option('-c', '--conf', help="指定配置文件")

    group = parser.add_option_group("驱动的显示/注册")
    group.add_option('-d', '--dump', nargs=0, help="注销驱动")
    group.add_option('-i', '--install', nargs=0, help="注册驱动")
    group.add_option('-f', '--file', help="指定驱动文件")
    group.add_option('-m', '--module', help="指定驱动模块")

    group = parser.add_option_group("工具类")
    group.add_option('', '--set-default', nargs=0, help="将dev-id指定的设备配置为默认设备")
    group.add_option('-e', '--empty', nargs=0, help="清理没有被引用的驱动文件")
    group.add_option('-p', '--purge', nargs=0, help="清空设备相关的数据库记录")
    group.add_option('-y', '--without-confirm', nargs=0, help="不需要确认")
    group.add_option('-l', '--list', nargs=0, help="显示已经注册的驱动列表")
    group.add_option('-g', '--msg', help="进程运行名")
    group.add_option('', '--uuid', help="进程运行标识")

    options, args = parser.parse_args()

    # 执行驱动服务
    if options.run is not None:
        if options.dev_id is None:
            print("运行驱动需要提供驱动/设备ID！")
            exit(-1)

        device_driver = get_device_driver(options.dev_id, options.conf)
        if device_driver is None:
            exit(-1)
        device_driver.run_until_exit()
    # 根据设备内部编号注销驱动
    elif options.uninstall is not None:
        if options.dev_id is None:
            print("注销驱动需要提供驱动/设备ID！")
            exit(-1)
        unregister_device_driver(options.dev_id)
    # 根据提供的文件注册设备驱动
    elif options.install is not None:
        if options.file is not None:
            register_device_driver_by_file(options.file)
        elif options.module is not None:
            register_device_driver_by_module(options.module)
        else:
            print("注册驱动需要指定驱动文件(-f)或模块(-m)")
        exit(-1)
    elif options.dump is not None:
        if options.file:
            dump_device_driver_by_zipfile(options.file)
        elif options.dev_id:
            dump_device_driver_by_device_id(options.dev_id)
        else:
            print("显示驱动内容需要指定驱动文件!")
            exit(-1)
    elif options.empty is not None:
        purge_unreferenced_driver_files()
    elif options.purge is not None:
        purge_device(options.without_confirm)
    elif options.list is not None:
        list_all_registered_device_driver()
    elif options.uninstall is not None:
        if options.dev_id is None:
            print("设置默认驱动需要提供驱动/设备ID！")
            exit(-1)
        set_device_as_default(options.dev_id)
    else:
        pass
