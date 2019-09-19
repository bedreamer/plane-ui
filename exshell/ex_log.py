# -*- coding: utf8 -*-
import plog

__doc__ = """系统日志控制指令集"""
__usage__ = __doc__ + """
Usage: log"""


def main(ctx, cmd, *args):
    try:
        plog.run_as_deamon()
    except KeyboardInterrupt:
        pass
