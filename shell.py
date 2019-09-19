# -*- coding: utf8 -*-
# 目的是提供一个控制整个系统的终端
# 所有的功能都抽象为指令，所有的操作也都由指令集和组成
import traceback
import re
import socket
import profile
import psutil
import sys
import os
import time
import codecs
import json
import redis
import importlib
import exshell


__version__ = 'v1.0'


class ShellContext:
    """shell执行的上下文"""
    def __init__(self):
        # sessionID
        self.sid = None

        # redis 服务器地址
        self.host = None
        # redis 服务器端口
        self.port = None
        # redis 数据库编号
        self.database = None
        # redis 服务器密码，没有密码保持空
        self.password = None

        # redis 链接句柄
        self.redis = None
        self.redis_connection_pool = None

    def do_connnect(self):
        """执行连接至服务器的动作"""
        if self.redis is not None:
            print("连接已经建立了.")
            return

        if self.host is None:
            print("** ERROR:需要指定host.")
            return

        if self.port is None:
            print("** ERROR:需要指定port.")
            return

        if self.database is None:
            print("** ERROR:需要指定database.")
            return

        try:
            redis_connection_pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password, db=self.database)
        except Exception as e:
            print("** ERROR:", e)
            return

        try:
            r = redis.Redis(connection_pool=redis_connection_pool)
        except Exception as e:
            print("** ERROR:", e)
            return

        try:
            r.llen('test connection status')
        except Exception as e:
            print("** ERROR:", e)
            return

        self.redis_connection_pool = redis_connection_pool
        self.redis = r

    def do_bind(self, sid):
        """绑定一个会话"""
        path = 'session-{}:etc'.format(sid)
        try:
            session_profile_bytes = self.redis.get(path)
            session_profile = json.loads(session_profile_bytes)
        except Exception as e:
            print("** ERROR:", e)
            return

        print("bind on {} as".format(path), session_profile)

    def do_start(self):
        """开始新的会话"""

    def do_close(self):
        """关闭当前连接"""
        if self.redis is None:
            print("** ERROR: 还没有连接")
            return

        self.redis_connection_pool.disconnect()
        self.redis = None
        self.redis_connection_pool = None

    def get_current_prompt(self):
        """获取提示符备注"""
        plane = 'Plane'
        if self.redis:
            return '{}@{}:{}-{}>'.format(plane, self.host, self.port, self.database)
        else:
            return '{}:blank>'.format(plane)


class PlaneTerminal:
    """
        Plane交互式终端
    """
    def __init__(self, prepare_command, *args):
        self.terminated = False

        # 运行上下文
        self.ctx = ShellContext()

        # 初始化完成后需要立即执行的命令
        self.prepare_commands = prepare_command

        # 执行run命令的脚本深度
        self.run_script_stack = list()

        # 扩展命令
        self._ex_shell = dict()
        self._ex_shell = self.load_all_exshell_command()

    def show_welcome_message(self):
        self.cmd_copyright('copyright')
        self.cmd_version('version')
        print('Type "help", "copyright" or "welcome" for more information.')

    def do_clean_up(self):
        pass

    def cmd_reload(self, cmd, *args):
        """重新加载扩展指令"""
        for _, module in self._ex_shell.items():
            del module

        self._ex_shell = self.load_all_exshell_command()

    def load_all_exshell_command(self):
        """加载全部扩展指令"""
        root = importlib.reload(exshell)

        _ex = dict()
        for name in root.__name__:
            module_name = '.'.join(['exshell', 'ex_' + name])
            try:
                if name in self._ex_shell:
                    module = importlib.reload(self._ex_shell[name])
                else:
                    module = importlib.import_module(module_name)
                _ex[name] = module
            except ImportError as e:
                pass

        return _ex

    def get_ex_shell_command(self, command):
        """获取扩展命令模块"""
        try:
            return self._ex_shell[command]
        except KeyError:
            module_name = '.'.join(['exshell', command])
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                return None

            self._ex_shell[command] = module
            return module

    def _process_builtin_command(self, line):
        """执行内置命令"""
        command_line = line.split(' ')
        command = command_line[0].lower()

        cb = self.__getattribute__('cmd_' + command)
        try:
            cb(*command_line)
        except Exception as e:
            print("inner error", e)

    def _process_exshell_command(self, line):
        """执行扩展shell命令"""
        command_line = line.split(' ')
        command = command_line[0].lower()

        module = self.get_ex_shell_command(command)
        if not module:
            return self._process_os_command(line)

        try:
            return module.main(self.ctx, *command_line)
        except Exception as e:
            print("invalid module command", command_line, e)
            return

    def _process_os_command(self, line):
        """执行操作系统命令"""
        os.system(line)

    def process_command_line(self, line):
        """执行命令行"""
        try:
            return self._process_builtin_command(line)
        except AttributeError:
            pass

        return self._process_exshell_command(line)

    def run_until_exit(self):
        """运行直到结束"""
        if not self.prepare_commands:
            self.show_welcome_message()
        else:
            for line in self.prepare_commands.split(';'):
                print("> ", line)
                self.process_command_line(line.lstrip().rstrip())
                if self.terminated:
                    break

            return self.do_clean_up()

        #readline.set_auto_history(True)
        while not self.terminated:
            prompt = self.ctx.get_current_prompt()
#            line = readline.get_line_buffer()
            line = input(prompt).lstrip().rstrip()
            if len(line) == 0:
                continue
            else:
                self.process_command_line(line)
                self.add_history(line)

        return self.do_clean_up()

    @staticmethod
    def add_history(line):
        path = '/'.join([profile.platform_work_dir, 'shell-history.txt'])
        with codecs.open(path, 'a+', encoding=profile.encoding) as file:
            file.write(line)
            file.write('\n')

    def cmd_connect(self, cmd):
        """连接至服务器"""
        return self.ctx.do_connnect()

    def cmd_bind(self, cmd, sid=None):
        """绑定一个会话"""
        if sid is None:
            print("** ERROR: 需要指定会话ID")
            return

        return self.ctx.do_bind(sid)

    def cmd_start(self, cmd):
        """创建一个会话"""
        return self.ctx.do_start()

    def cmd_close(self, cmd):
        """关闭当前的连接"""
        return self.ctx.do_close()

    def dump_run_script_stack(self):
        """展示脚本执行的调用顺序"""
        print("run 调用顺序:")
        for i, record in enumerate(self.run_script_stack):
            print("   " * (i + 1), record['name'], ', line', record['line'])

    def cmd_run(self, cmd, script_name=None):
        """执行脚本"""
        if script_name is None:
            print("** ERROR: 需要指定脚本名")
            return

        """执行指定名称的脚本文件"""
        if len(self.run_script_stack) > 10:
            print("** ERROR: 执行script深度超过10层.")
            for record in self.run_script_stack:
                print(str(record['line']).ljust(9), record['name'])
            return

        if len(self.run_script_stack) == 0:
            record = {'name': script_name, 'line': 0}
            self.run_script_stack.append(record)

        if os.path.isabs(script_name):
            full_script_path = script_name
        else:
            full_script_path = '/'.join([profile.platform_profile_dir, 'shell', script_name])

        suffix = '.script'
        if full_script_path[::-1].find(suffix[::-1]) != 0:
            full_script_path += suffix

        if os.path.exists(full_script_path):
            with codecs.open(full_script_path, mode='r', encoding=profile.encoding) as file:
                line_number = 0
                for line in file.readlines():
                    line = line.lstrip().rstrip()
                    line_number += 1
                    if len(line) == 0:
                        continue

                    if line[0] == '#':
                        continue

                    if line.lower().find('run') == 0:
                        record = {'name': script_name, 'line': line_number}
                        self.run_script_stack.append(record)

                    self.process_command_line(line)
        else:
            record = self.run_script_stack[-1]
            print("** ERROR: {} ({}) 没有找到".format(script_name, full_script_path))
            #print("   深度: ", len(self.run_script_stack))
            #print("   脚本名: {}".format(record['name']))
            #print("   行号: ", record['line'])

            if len(self.run_script_stack) > 1:
                self.dump_run_script_stack()

        # 删除最后一个
        self.run_script_stack.pop()

    def cmd_host(self, cmd, host=None):
        """获取目标地址或设定目标地址"""
        if host is None:
            print(self.ctx.host)
        else:
            if host != self.ctx.host:
                try:
                    real_host = socket.gethostbyname(host)
                except socket.gaierror:
                    print("无法为地址{}解析DNS，明确指定IP地址".format(host))
                    return
            else:
                print("host {} not changed.".format(self.ctx.host))
                return

            print("host change from {} to {}".format(self.ctx.host, real_host))
            self.ctx.host = real_host

    def cmd_port(self, cmd, port=None):
        """获取目标端口或设定目标端口"""
        if port is None:
            print(self.ctx.port)
        else:
            try:
                real_port = int(port)
            except ValueError:
                print("正确的端口参数为整数，范围：0～65535")
                return

            if real_port <= 0 or real_port > 6535:
                print("正确的端口范围：0～65535，给定值:", port)
                return

            if real_port != self.ctx.port:
                print("port change from {} to {}".format(self.ctx.port, real_port))
            else:
                print("port {} not changed.".format(self.ctx.host))
                return

            self.ctx.port = real_port

    def cmd_database(self, cmd, database=None):
        """获取数据库编号或设定据库编号"""
        if database is None:
            print(self.ctx.database)
        else:
            try:
                real_database = int(database)
            except ValueError:
                print("正确的数据库编号为整数，范围：0～16")
                return

            if real_database < 0 or real_database > 16:
                print("正确的数据库编号范围：0～16，给定值:", database)
                return

            if real_database != self.ctx.database:
                print("database change from {} to {}".format(self.ctx.database, real_database))
            else:
                print("database {} not changed.".format(self.ctx.database))
                return

            self.ctx.database = real_database

    def cmd_sleep(self, cmd, ms=None):
        """休眠指定的毫秒数"""
        if ms is None:
            print("** ERROR: sleep 需要参数")
            return

        seconds = int(ms) / 1000.0
        if seconds < 0:
            print("** 休眠时间 大于等于0")
            return

        time.sleep(seconds)

    def cmd_echo(self, cmd, *args):
        """回显字符串"""
        if len(args) == 0:
            msg = ''
        else:
            msg = ' '.join(args)

        print(msg)

    def cmd_info(self, cmd):
        """显示当前shell的状态"""
        print("命令行：", ' '.join(sys.argv))
        print("版本：", __version__)
        print("PID：", os.getpid())
        print("工作路径：", os.getcwd())
        print("安装路径：", profile.platform_root_dir)
        print("目标主机：", self.ctx.host if self.ctx.host == profile.redis_host else "{} ({})".format(self.ctx.host, profile.redis_host))
        print("目标端口：", self.ctx.port)
        print("目标数据库编号：", self.ctx.database)
        print("链接状态：", "Established" if self.ctx.redis else "Disconnected")

    def cmd_version(self, cmd):
        """显示shell版本号"""
        print('Plane', __version__)

    def cmd_copyright(self, cmd):
        """显示版权信息"""
        print("Plane Interactive Shell by Lijie (C) 2019 ALL Right Reserved.")

    def cmd_welcome(self, cmd):
        """显示welcome文本"""
        self.show_welcome_message()

    def cmd_exit(self, cmd):
        """
        退出当前shell
        这是详细说明
        """
        self.terminated = True

    def _show_all_command_help(self):
        r = re.compile(r'cmd_.+')

        print("build in command list:")
        for node in self.__dir__():
            if r.match(node) is None:
                continue

            interface = self.__getattribute__(node)

            if not callable(interface):
                continue

            # 第一行是帮助的摘要信息
            if interface.__doc__:
                doc = interface.__doc__.lstrip().split('\n')[0]
            else:
                doc = '** 没有提供文档 **'

            cmd = node[4:]
            print(cmd.ljust(16), doc)

        print()
        print("extend command list:")
        for name, module in self._ex_shell.items():
            try:
                usage = module.__doc__
                if usage is None:
                    raise AttributeError
            except AttributeError:
                usage = '** 没有提供文档 **'

            print(name.ljust(16), usage)

    def cmd_help(self, cmd, *args):
        """显示帮助信息"""

        if len(args) == 0:
            return self._show_all_command_help()

        target = args[0].lower()
        if target in self._ex_shell:
            try:
                usage = self._ex_shell[target].__usage__
            except AttributeError:
                usage = self._ex_shell[target].__doc__

            if usage is None:
                usage = '** 没有提供文档 **'

            print(usage)


def create_interactive_terminal(*args):
    return PlaneTerminal(*args)


if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser(usage='%prog [Command|--help] {Options}')

    group = parser.add_option_group("Command")
    group.add_option('-H', '--redis-host', default='127.0.0.1', help="目标地址")
    group.add_option('-P', '--redis-port', default=6379, type='int', help="目标端口")
    group.add_option('-D', '--redis-database', default=0, type='int', help="目标数据库编号")
    group.add_option('-C', '--command', help="执行由;分割的指令后退出")

    options, args = parser.parse_args()

    redis_host = options.redis_host
    redis_port = options.redis_port
    redis_database = options.redis_database
    _prepare_command = options.command

    shell = create_interactive_terminal(_prepare_command)
#    shell = create_interactive_terminal(redis_host, redis_port, redis_database, prepare_command)
    shell.run_until_exit()
