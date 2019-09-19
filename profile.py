# -*- coding: utf8 -*-
import os
import codecs
import json
import redis
import sys
import hashlib
import django
from django.core.exceptions import AppRegistryNotReady, ImproperlyConfigured
from django.apps import apps


def is_release_mode():
    """
    判断当前是否在发布模式，发布模式使用pyc进行执行
    :return:
        True: 发布模式
        False：调试模式
    """
    py_file = sys.argv[0][::-1]
    if py_file.find('.pyc'[::-1]) == 0:
        return True
    return False


try:
    apps.check_apps_ready()
except (AppRegistryNotReady, ImproperlyConfigured):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()


# python可执行程序路径
python_executable_path = sys.executable

# 设备驱动文件
device_driver_manager_script = 'devd.py' if not is_release_mode() else 'devd.pyc'
# 项目管理执行文件
project_manager_script = 'prjd.py' if not is_release_mode() else 'prjd.pyc'
# plane管理执行文件
plane_manager_script = 'plane.py' if not is_release_mode() else 'plane.pyc'
# log管理执行文件
log_manager_script = 'plog.py' if not is_release_mode() else 'plog.pyc'
# 流程管理执行文件
flowd_manager_script = 'flowd.py' if not is_release_mode() else 'flowd.pyc'


# 平台软件的根目录
platform_root_dir = os.path.dirname(os.path.abspath(__file__))
# 平台软件的工作目录
platform_work_dir = platform_root_dir
# 配置数据的存储目录
platform_profile_dir = '/'.join([platform_root_dir, 'etc'])
# 流程文件的存储目录
flowfile_storage_dir = '/'.join([platform_profile_dir, 'flows'])
# 支持的设备配置数据的存储目录
platform_device_dir = '/'.join([platform_profile_dir, 'devices'])
# 支持的设备驱动目录
platform_device_drivers_dir = '/'.join([platform_root_dir, 'drivers'])
# 用户项目数据存储目录
project_documents_dir = '/'.join([platform_root_dir, 'projects'])
# 平台日志数据存储目录
project_log_dir = '/'.join([platform_root_dir, 'log'])


# 默认文件编码
encoding = 'utf8'
# 默认的文件权限掩码
default_file_mode = 0o644
# 默认的目录权限掩码
default_dir_mode = 0o755

redis_host = '127.0.0.1'
# redis_host = 'cbd-mall.vip'
redis_port = 6379
redis_db = 0

# 时间日期默认格式
DT_FORMAT = '%Y-%m-%d %H:%M:%S'
DT_TIMESTAMP = '%Y%m%d%H%M%S'


#  驱动文件后缀名
DRV_FILE_SUFFIX = '.zip'
#  流程文件后缀名
FLOW_FILE_SUFFIX = '.xlsx'


# redis键过期时间, 默认为5秒，一般用于对时效性有要求的功能，例如设备profile等
KEY_EXPIRE = 5

# 最大日志文件大小
LOG_FILE_MAX_SIZE = 1 * 1024 * 1024
# 错误日志文件记录路径
error_log_entry_file = '/'.join([project_log_dir, 'error.log'])

# 默认的主循环周期毫秒数
DEFAULT_MAIN_LOOP_PERIOD_IN_MS = 1000


# 项目状态列表
PRJ_STATUS_INIT = '初始化'
PRJ_STATUS_CONFIGURE = '配置'
PRJ_STATUS_READY = '就绪'
PRJ_STATUS_RUNNING = '执行'
PRJ_STATUS_PAUSE = '暂停'
PRJ_STATUS_DONE = '完成'
PRJ_STATUS_ABORT = '中止'
PRJ_STATUS_END = '结束'
PROJECT_STATUS_LIST = [
    PRJ_STATUS_INIT,
    PRJ_STATUS_CONFIGURE,
    PRJ_STATUS_READY,
    PRJ_STATUS_RUNNING,
    PRJ_STATUS_PAUSE,
    PRJ_STATUS_DONE,
    PRJ_STATUS_ABORT,
    PRJ_STATUS_END
]

# 项目状态转移路由
PROJECT_STATUS_CHANGE_ROUTE = {
    '初始化': ['配置'],
    '配置': ['就绪', '中止'],
    '就绪': ['执行', '中止'],
    '执行': ['暂停', '中止', '完成'],
    '暂停': ['执行', '中止'],
    '中止': ['结束'],
    '完成': ['结束'],
    '结束': []
}


# Redis连接池
_redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
# 公共redis连接
public_redis = redis.Redis(connection_pool=_redis_pool)


def alloc_redis():
    """获取缓存对象"""
    return redis.Redis(connection_pool=_redis_pool)


def alloc_subscriber():
    """获取一个订阅器"""
    return redis.client.PubSub(connection_pool=_redis_pool)


def alloc_publisher():
    """获取一个发布器"""
    return redis.client.PubSub(connection_pool=_redis_pool)


if not os.path.exists(platform_profile_dir):
    os.mkdir(platform_profile_dir, default_dir_mode)


if not os.path.exists(project_documents_dir):
    os.mkdir(project_documents_dir, default_dir_mode)


if not os.path.exists(platform_device_dir):
    os.mkdir(platform_device_dir, default_dir_mode)


if not os.path.exists(project_log_dir):
    os.mkdir(project_log_dir, default_dir_mode)


if not os.path.exists(platform_device_drivers_dir):
    os.mkdir(platform_device_drivers_dir, default_dir_mode)
    package_file = '/'.join([platform_device_drivers_dir, '__init__.py'])
    with codecs.open(package_file, 'w', encoding=encoding) as file:
        pass


def join_default_work_dir(entry):
    """生成默认目录下的新节点"""
    return '/'.join([platform_work_dir, entry])


def reset_default_work_dir():
    """复位工作目录到默认"""
    os.chdir(platform_work_dir)


def join_profile_dir(entry):
    return '/'.join([platform_profile_dir, entry])


def get_log_path():
    """获取日志记录路径"""
    return ':'.join(['plane', 'log'])


"""-----设备相关路径-----"""


def get_device_profile_path(dev_type):
    """返回设备的配置数据路径"""
    return ':'.join([dev_type.lower(), 'profile'])


def get_device_yc_path(dev_type):
    """返回设备的遥测数据路径"""
    return ':'.join([dev_type.lower(), 'data-register'])


def get_device_yx_path(dev_type):
    """返回设备的遥信数据路径"""
    return get_device_yc_path(dev_type)


def get_device_control_path(dev_type):
    """返回设备设置参数的路径, 例如设备的遥调，遥控值"""
    return ':'.join([dev_type.lower(), 'control-register'])


def get_device_control_command_path(dev_type):
    """设备控制路径"""
    return ':'.join([dev_type.lower(), 'control-cmd'])


"""-----流程相关路径-----"""


def get_flow_status_path():
    """获取流程控制路径"""
    return ':'.join(['flow', 'status'])


def get_flow_source_context_path():
    """获取流程源码"""
    return ':'.join(['flow', 'source'])


def get_flow_control_path():
    """获取流程状态路径"""
    return ':'.join(['flow', 'control'])


"""-----项目相关路径-----"""


def get_project_status_path():
    """获取项目状态路径"""
    return ':'.join(['project', 'status'])


def get_project_control_path():
    """获取项目控制路径"""
    return ':'.join(['project', 'control'])


def get_project_storage_node(prj_id):
    """获取存储名"""
    return 'prj-{}'.format(str(prj_id).rjust(6, '0'))


def calc_file_md5sum(file_path):
    """计算给定路径的文件MD5值"""
    md5 = hashlib.md5()
    with codecs.open(file_path, mode='rb') as f:
        while True:
            b = f.read(10 * 1024)
            if not b:
                break
            md5.update(b)

    return md5.hexdigest()
