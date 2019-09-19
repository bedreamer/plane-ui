# plane-纸飞机

纸飞机软件是一款用于集成实验室设备的自动化控制软件。目前可以集成进来的设备包含：
1. 电池管理系统（BMS）
2. 水冷机
3. 充放电设备
4. 环境仓
5. 振动台

软件按模块划分包含：
1. redis数据缓存模块
2. 用户操作接口模块(图形化)
3. 交互式操作接口模块（终端shell）
4. 自动流程执行模块
5. 设备注册模块
6. 设备驱动模块（采集，控制）

## 概念
软件使用以项目进行分类，例如实验分为电池性能试验、安全性实验、环境适应能力实验等
项目的状态包含：初始化， 配置，就绪，执行，暂停，完成，中止 ，结束。状态机流向为:

    初始化 --->  配置
    配置   --->  就绪
    就绪   --->  执行
    执行   --->  暂停, 中止, 完成
    暂停   --->  执行, 中止
    中止   --->  结束
    完成   --->  结束 
 

## 主要文件及目录
### profile.py
系统全部运行的配置参数获取点，其他功能模块采用 **import** 方式进行引用，注意需要和python内建profile库进行区分。
    
    import profile
    
    # 引用redis服务器地址， 等等
    profile.redis_host
    ....

### devd.py 
设备驱动管理程序，包含驱动的执行、注册（更新）、注销、显示功能

#### 查看帮助
    python devd.py --help

#### 执行驱动
    python devd.py --run --dev-id driver-id

#### 注册/更新驱动(文件模式)
    python devd.py --install --file path-to-driver-file.zip

#### 注册/更新驱动(模块模式)
    python devd.py --install --module module-name

#### 注销驱动
    python devd.py --uninstall --dev-id driver-id

#### 通过ID显示驱动
    python devd.py --dump --dev-id driver-id

#### 通过文件显示驱动
    python devd.py --dump --file path-to-driver-file.zip

#### 列出全部已注册的驱动
    python devd.py --list

#### 设置默认设备
    python devd.py --set-default --dev-id driver-id


### plog.py
系统日志检视模块，也可单独用于日志的监视

    import plog
    
    # 普通记录日志
    plog.info("这个级别是信息级别")
    plog.debug("这个级别是调试级别")
    plog.warn("这个级别是警告级别")
    plog.error("这个级别是错误级别")

    # 添加额外的字段，通过指定命名参数来记录特殊的日志
    plog.info("这个级别是信息级别", target='水冷机')

### shell.py
交互式操作接口模块，提供一个命令行式的交互终端, 具体操作指令可以按照 **help** 进行查询，支持内建命令，操作系统命令，redis命令
    
    python shell.py

    ps 命令用于显示跟该系统相关的全部进程
    > ps
    kill 用于终止指定的程序, 提供的name是脚本名称
    > kill pid/name


### flowd.py
自动流程执行服务程序，程序启动后保持服务状态，直到接收到停止指令，主要功能是相应用户提出的自动流程控制请求

    python flowd.py


### prjd.py
项目总状态服务程序，作为所有功能的入口，这个程序是和界面服务器程序并列的级别。

#### 启动项目服务
    python prjd.py --start
    
#### 停止项目服务
    python prjd.py --stop

#### 重启项目服务
    python prjd.py --restart

#### 显示项目服务状态
    python prjd.py --status

#### 显示项目列表
    python prjd.py --list

#### 罗列项目信息
    python prjd.py --dump --project-id project-id

#### 创建项目
    python prjd.py --create --project-name name --lab-sn sn --subscript subscript --description description

#### 清理全部项目数据(带人工确认)
    python prjd.py --purge

#### 清理全部项目数据(无需确认)
    python prjd.py --purge --without-confirm

#### 绑定设备
    python prjd.py --bind-device --project-id project-id --device-id device-id

#### 解绑设备
    python prjd.py --unbind-device --project-id project-id --device-id device-id


### api.py
模块操作redis或者模块间通讯的简单接口，定义了api返回格式

    status, payload, reason = api.function_name(...)
    status: api的执行结果状态，只能是 **ok** 或 **error**
    payload: api返回的数据体，仅在status为 ok 时保证这个payload有效
    reason: api调用错误后给定一个具体的错误原因，用于排错

提供模块和redis之间进行进行通讯的基本协议，包含的主要结构有： 

    [1] Request(请求协议)
    [2] Response(应答协议)
请求协议和应答协议必须成对匹配出现。
