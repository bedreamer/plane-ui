# -*- coding: utf-8 -*-
import sys
import os
import profile


__doc__ = """设备操作指令集"""
__usage__ = """"""


def main(ctx, cmd, *args):
    execute_path = ''.join(['"', sys.executable, '"'])

    devd_py = '/'.join([profile.platform_root_dir, profile.device_driver_manager_script])
    devd_py_path = ''.join(['"', devd_py, '"'])

    command = [execute_path, devd_py_path]
    command.extend(args)

    command_line = ' '.join(command)

    os.system(command_line)

