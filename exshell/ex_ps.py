# -*- coding: utf8 -*-
# author: lijie
import re
import os
import psutil
import profile


__doc__ = """列出系统中关联的所有python进程"""
__usage__ = __doc__


def yield_ps_from_system():
    r = re.compile('^python')

    def is_relative(ps):
        if r.match(ps.name().lower()) is None:
            return False

        ps_cwd = ps.cwd()
        if ps_cwd.find(profile.platform_root_dir) != 0:
            return False

        ps_command_line = ps.cmdline()
        try:
            script_file = ps_command_line[1]
        except IndexError:
            return False

        if os.path.isabs(script_file):
            script_file_abs_path = script_file
        else:
            script_file_abs_path = '/'.join([ps_cwd, script_file])

        if script_file_abs_path.find(profile.platform_root_dir) != 0:
            return False

        return True

    relative_processes_list = [ps for ps in psutil.process_iter() if is_relative(ps)]
    for i, ps in enumerate(relative_processes_list):
        script_command_line = ps.cmdline()[1:]
        idx = i + 1
        pid = ps.pid
        script = ' '.join(script_command_line)
        if os.path.isabs(script):
            if script.find(profile.platform_root_dir) == 0:
                script = script[len(profile.platform_root_dir) + 1:]
        working_dir = ps.cwd()
        yield idx, pid, script, working_dir


def main(cmd, *args):
    ps_list = list(yield_ps_from_system())

    if len(ps_list):
        print("根工作目录:", profile.platform_root_dir)
        print("Python:", profile.python_executable_path)
        print("#".center(3), "PID".ljust(8), "COMMAND LINE")
        print("=" * 30)

    for idx, pid, script, working_dir in ps_list:
        if working_dir != profile.platform_root_dir:
            print(str(idx).center(3), str(pid).ljust(8), script, working_dir)
        else:
            print(str(idx).center(3), str(pid).ljust(8), script)
