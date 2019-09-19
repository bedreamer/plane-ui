# -*- coding: utf8 -*-
# author: lijie
import os
import platform


__doc__ = """执行系统命令"""
__usage__ = __doc__


def main(ctx, cmd, *args):
    if len(args):
        try:
            os.system(' '.join(args))
        except Exception as e:
            print(e)
    else:
        print(platform.system())
