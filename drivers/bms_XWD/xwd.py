# -*- coding: utf-8 -*-
# 这个文件提供了一个设备驱动模板
import profile
import api
import time
import os
import sys
import random
import json
import plog
import cantools


def device_read_all_register(channel):
    signals = channel.read(1)
    if signals:
        channel.update_signal(signals)
