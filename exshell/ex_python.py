# -*- coding: utf-8 -*-
import profile
import sys
import os


__doc__ = """平台默认python操作接口"""
__usage__ = __doc__ + """
Usage: python [command] {parameters}"""


def main(ctx, cmd, *args):
    if ' ' in sys.executable:
        execute_path = ''.join(['"', sys.executable, '"'])
    else:
        execute_path = sys.executable

    command = [execute_path]
    command.extend(args)
    command_line = ' '.join(command)
    os.system(command_line)
