# -*- coding: utf-8 -*-


class DeviceBasic(object):
    """设备基类"""
    def __init__(self):
        pass

    def open(self):
        """打开设备"""
        raise NotImplementedError

    def close(self):
        """关闭设备"""
        raise NotImplementedError


class DeviceFunction(dict):
    """设备支持的函数"""
    def __init__(self, name, typo, valid_range, valid_string, comment=None, unit=None):
        if comment is None:
            comment = ''
        if unit is None:
            unit = ''

        super().__init__(name=name, type=typo, valid_range=valid_range, valid_string=valid_string, comment=comment, unit=unit)


class DeviceFunctionSet:
    """设备功能集合"""
    def __init__(self):
        pass


class DeviceRegister(dict):
    """设备支持的寄存器"""
    def __init__(self, name, typo, valid_range, valid_string, comment=None, unit=None):
        if comment is None:
            comment = ''
        if unit is None:
            unit = ''

        super().__init__(name=name, type=typo, valid_range=valid_range, valid_string=valid_string, comment=comment, unit=unit)


class DeviceInputRegister(DeviceRegister):
    """数据寄存器，用于保存设备的运行遥测和遥信数据"""
    pass


class DeviceHoldRegister(DeviceRegister):
    """保持寄存器，用于存放设备的遥调和遥控参数"""
    pass


class DeviceRegisterSet:
    """设备寄存器集合"""
    def __init__(self):
        pass
