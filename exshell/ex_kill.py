# -*- coding: utf8 -*-
import os
import codecs
import subprocess
import signal
import platform
import exshell.ex_ps as ps


__doc__ = """给进程发送停止信号"""
__usage__ = __doc__ + """
Usage:
    kill [pid]"""


def kill_process_by_pid(pid):
    """以PID搜索方式关闭进程"""
    if platform.system().lower() != 'windows':
        os.kill(pid, signal.SIGTERM)
        return

    # fucking windows
    cmd = 'taskkill.exe /PID {} /F'.format(pid)
    with subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except:
            process.kill()
            process.wait()


def kill_process_by_name(name):
    """以进程名搜索方式关闭进程"""
    for _, pid, script, working_dir in ps.yield_ps_from_system():
        if script == name:
            kill_process_by_pid(pid)
        elif script.find(name) == 0:
            line = input("确定终止进程{}, pid={} (N/y):".format(script, pid)).lower().lstrip()

            if len(line) and line[0] == 'y':
                kill_process_by_pid(pid)
            else:
                continue


def main(ctx, cmd, *args):
    """发送停止信号"""
    if len(args) == 0:
        print(__usage__)
        return

    try:
        pid = int(args[0])
        return kill_process_by_pid(pid)
    except ValueError:
        name = args[0]
        return kill_process_by_name(name)
