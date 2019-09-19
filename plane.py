# -*- coding: utf-8 -*-
import sys
import os
import time
import profile
import psutil
import platform
import subprocess


Python = profile.python_executable_path
WorkingDirectory = profile.platform_root_dir


K_WD = 'working directory'
K_CMD = 'command line'
K_UUID = 'uuid'


services = {
#    "UI": {
#        "working directory": WorkingDirectory,
#        "command line": ' '.join([Python, "manager.py", 'runserver', "127.0.0.1:8000"])
#    },
    "plog": {
        K_UUID: '066c2c48-be8d-11e9-b12a-802bf9b7a34a',
        K_WD: WorkingDirectory,
        K_CMD: [Python, "plog.py"]
    },
    "flowd": {
        K_UUID: '148e6dee-be8d-11e9-a8be-802bf9b7a34a',
        K_WD: WorkingDirectory,
        K_CMD: [Python, "flowd.py"]
    },
}


def is_process_alive(uuid):
    """
    判断进程是否存在, 若进程存在返回PID，否则返回-1
    """
    for process in psutil.process_iter():
        try:
            script_command_line = ''.join(process.cmdline()[1:])
        except psutil.AccessDenied:
            continue

        if script_command_line.find(uuid) >= 0:
            return process.pid
    return -1


def get_process_pid(uuid):
    return is_process_alive(uuid)


"""  windows 平台相关函数  """


def windows_create_process(uuid, commandline, cwd):
    """在windows系统上创建进程"""
    subprocess.Popen(commandline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    return get_process_pid(uuid)


def windows_kill_process(uuid, pid):
    """在windows系统上停止进程"""
    command = ['taskkill', '/F', '/PID', str(pid)]
    os.system(' '.join(command))
    return get_process_pid(uuid)


"""  类Unix 平台相关函数  """


def unix_create_process(uuid, commandline, cwd):
    """在类unix系统上创建进程"""
    os.chdir(cwd)
    commandline += '&'
    os.system(commandline)

    return is_process_alive(uuid)


def unix_kill_process(uuid, pid):
    """在类unix系统上停止进程"""
    command = ['kill', '-9', str(pid)]
    os.system(' '.join(command))
    return is_process_alive(uuid)


"""  以下是平台无关函数  """


def create_process(uuid, commandline, cwd):
    if platform.system().lower() == 'windows':
        return windows_create_process(uuid, commandline, cwd)
    else:
        return unix_create_process(uuid, commandline, cwd)


def stop_process(uuid, pid):
    repeat = 3
    target = 0

    while repeat > 0 and target != -1:
        repeat -= 1
        if platform.system().lower() == 'windows':
            target = windows_kill_process(uuid, pid)
        else:
            target = unix_kill_process(uuid, pid)
        time.sleep(0.1)
        print(target)

    return target


"""  以下是服务相关的函数  """


def service_start_by_name(name):
    """创建进程，返回PID"""
    conf = services[name]
    uuid = conf[K_UUID]
    cwd = conf[K_WD]

    pid = is_process_alive(uuid)
    if pid > 0:
        return pid

    command_pairs = conf[K_CMD][::]
    command_pairs.extend(['--uuid', uuid])
    command_line = ' '.join(command_pairs)

    return create_process(uuid, command_line, cwd)


def service_stop_by_name(name):
    """停止进程"""
    conf = services[name]
    uuid = conf[K_UUID]
    target_pid = is_process_alive(uuid)
    if target_pid < 0:
        return

    pid = stop_process(name, target_pid)

    if pid > 0:
        print("停止进程<{}>失败，pid={}".format(name, target_pid))
    else:
        print("停止进程<{}>成功，pid={}".format(name, target_pid))


def service_restart_by_name(name):
    """根据名称重启进程"""
    service_stop_by_name(name)
    return service_start_by_name(name)


def service_status_by_name(name):
    """根据名称显示进程状态"""
    pid = is_process_alive(name)
    if pid > 0:
        print("进程 <{}> 运行中， pid={}".format(name, pid))
    else:
        print("进程 <{}> 未启动".format(name))


def services_start_all():
    """启动所有服务"""
    for name in services.keys():
        service_start_by_name(name)


def services_stop_all():
    """停止所有服务"""
    for name in services.keys():
        service_stop_by_name(name)


def services_restart_all():
    """重启所有服务"""
    for name in services.keys():
        pid = service_restart_by_name(name)
        if pid:
            print("重启进程: {} 成功, pid: {}".format(name, pid))


def services_status_all():
    """显示所有服务的进程状态"""
    for name in services.keys():
        service_status_by_name(name)


if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser(usage='%prog [Command|--help] {Options}')

    group = parser.add_option_group("服务管理")
    group.add_option('', '--start', nargs=0, help="启动服务，若不指定service-name则全部启动")
    group.add_option('', '--stop', nargs=0, help="停止服务，若不指定service-name则全部停止")
    group.add_option('', '--restart', nargs=0, help="重启服务，若不指定service-name则全部重启")
    group.add_option('', '--status', nargs=0, help="显示服务信息，若不指定service-name则显示全部")
    group.add_option('-n', '--name', help="指定项目")

    opt, args = parser.parse_args()
    if opt.start is not None:
        if opt.name is None:
            services_start_all()
        else:
            if opt.name.lower() not in services:
                print("没有服务 <{}>".format(opt.name))
                exit(0)
            service_start_by_name(opt.name)
    elif opt.stop is not None:
        if opt.name is None:
            services_stop_all()
        else:
            if opt.name.lower() not in services:
                print("没有服务 <{}>".format(opt.name))
                exit(0)
            service_stop_by_name(opt.name)
    elif opt.restart is not None:
        if opt.name is None:
            services_restart_all()
        else:
            if opt.name.lower() not in services:
                print("没有服务 <{}>".format(opt.name))
                exit(0)
            service_restart_by_name(opt.name)
    elif opt.status is not None:
        if opt.name is None:
            services_status_all()
        else:
            if opt.name.lower() not in services:
                print("没有服务 <{}>".format(opt.name))
                exit(0)
            service_status_by_name(opt.name)
