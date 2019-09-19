# -*- coding: utf-8 -*-
import profile
import sys
import os


__doc__ = """项目服务操作接口"""
__usage__ = __doc__ + """
Usage: project [command] {parameters}"""


def main(ctx, cmd, *args):
    if ' ' in sys.executable:
        execute_path = ''.join(['"', sys.executable, '"'])
    else:
        execute_path = sys.executable

    devd_py = '/'.join([profile.platform_root_dir, profile.plane_manager_script])
    devd_py_path = ''.join(['"', devd_py, '"'])

    command = [execute_path, devd_py_path]
    command.extend(args)

    command_line = ' '.join(command)

    os.system(command_line)
