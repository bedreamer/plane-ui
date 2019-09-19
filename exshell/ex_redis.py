# -*- coding: utf8 -*-
# author: lijie
import json
import profile


__doc__ = """执行Redis命令"""
__usage__ = __doc__


def main(ctx, cmd, *args):
    if len(args) == 0:
        return

    r = profile.public_redis
    try:
        func = r.__getattribute__(args[0])
    except Exception as e:
        print(e)
        return

    try:
        al = list(args)
        al.pop(0)
        result = func(*al)
    except Exception as e:
        print(e)
        return

    try:
        if isinstance(result, list):
            for idx, body in enumerate(result):
                print(idx + 1, body.decode())
        elif isinstance(result, bytes):
            body = json.loads(result)
            print(body)
        else:
            print(result)
    except Exception as e:
        print(e)
        print("Origin payload:")
        print(result.decode())

