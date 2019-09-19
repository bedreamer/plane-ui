# -*- coding: utf8 -*-


__doc__ = """扫描并展示会话列表"""
__usage__ = __doc__ + """
Usage: scan"""


def main(ctx, cmd, *args):
    if ctx.redis is None:
        print("** ERROR: 需要先执行connect.")
        return

    pattern = 'session-*'
    session_path_list = ctx.redis.keys(pattern)
    if len(session_path_list):
        print("#".ljust(8), "SID")
        print("=" * 20)

    sid_set = {path.decode()[8:].split(':')[0] for path in session_path_list}
    for idx, sid in enumerate(sid_set):
        print(str(idx + 1).ljust(8), sid)
