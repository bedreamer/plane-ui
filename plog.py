# -*- coding: utf-8 -*-
# author: lijie
import json
import time
import sys
import profile
import api


def dump_payload(payload):
    prog = payload['$_prog']
    lv = payload['$_lv']
    msg = payload['$_msg']
    tsp = payload['$_tsp']

    del payload['$_prog']
    del payload['$_lv']
    del payload['$_msg']
    del payload['$_tsp']

    print(lv, prog, ''.join(['[', tsp, ']']), msg)
    if len(payload) > 0:
        json.dump(payload, fp=sys.stdout, indent=2, ensure_ascii=False, default=lambda o: o.__dict__)
        print()


def log_something(lv, *args, **kwargs):
    public = {
        '$_prog': sys.argv[0],
        '$_lv': lv,
        '$_tsp': time.strftime(profile.DT_FORMAT),
        '$_msg': ''.join(args),
    }

    payload = dict(public, **kwargs)
    _log_path = profile.get_log_path()
    status, _, reason = api.rpush(_log_path, payload)
    if status != api.OK:
        print(reason)

    dump_payload(payload)


def error(*args, **kwargs):
    return log_something('error', *args, **kwargs)


def warn(*args, **kwargs):
    return log_something('warn', *args, **kwargs)


def info(*args, **kwargs):
    return log_something('info', *args, **kwargs)


def debug(*args, **kwargs):
    return log_something('debug', *args, **kwargs)


def run_as_deamon():
    print("log printer at host", profile.redis_host)

    _r = profile.public_redis
    _log_path = profile.get_log_path()

    while True:
        log_payload = _r.lpop(_log_path)
        if log_payload is None:
            time.sleep(1)
            continue

        payload = json.loads(log_payload.decode(), encoding=profile.encoding)
        dump_payload(payload)


def main(ctx, cmd, *args):
    run_as_deamon()


if __name__ == '__main__':
    run_as_deamon()
