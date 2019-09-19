# -*- coding: utf-8 -*-
# author: lijie
from django.urls import path, include, reverse
from django.shortcuts import render
from django.http import *
from storage.models import *
import api as api
import os
import tempfile
import codecs



def show_project_device_summary(request, prj_id):
    """显示项目关联设备的摘要信息"""
    context = dict()

    # 获取项目相关的服务状态
    status, xm_fwzt_list, reason = api.project_service_status(prj_id)
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "未通讯/或sid错误")
    else:
        for xm_fwzt in xm_fwzt_list :
            for i in xm_fwzt.keys():
                if i == "dev_type":
                    if xm_fwzt[i] == "ec":
                        for i in xm_fwzt.keys():
                            if i == "服务中":
                                ec_zt = xm_fwzt[i]
                                ec_qd_zt = {"驱动状态": ec_zt}
                                context['ec_qd_zt'] = ec_qd_zt
                    elif xm_fwzt[i] == "cd":
                        for i in xm_fwzt.keys():
                            if i == "服务中":
                                cd_zt = xm_fwzt[i]
                                cd_qd_zt = {"驱动状态": cd_zt}
                                context['cd_qd_zt'] = cd_qd_zt
                    elif xm_fwzt[i] == "cm":
                        for i in xm_fwzt.keys():
                            if i == "服务中":
                                cm_zt = xm_fwzt[i]
                                cm_qd_zt = {"驱动状态": cm_zt}
                                context['cm_qd_zt'] = cm_qd_zt
                    elif xm_fwzt[i] == "bms":
                        for i in xm_fwzt.keys():
                            if i == "服务中":
                                bms_zt = xm_fwzt[i]
                                bms_qd_zt = {"驱动状态": bms_zt}
                                context['bms_qd_zt'] = bms_qd_zt


    # 获取项目绑定水冷机设备信息
    status, bd_cm_list, reason = api.project_get_device_by_type(prj_id, "cm")
    if status != api.OK:
        cm_sign = {"绑定cm设备状态":"没绑定"}
        context['cm_sign'] = cm_sign
    else:
        cm_sign = {"绑定cm设备状态": "绑定"}
        context['cm_sign'] = cm_sign
        # 获取水冷机设备遥信数据
        status, cm_yx, reason = api.device_get_yx("cm")
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            context['cm_yx'] = cm_yx
        # 获取水冷机设备遥测数据
        status, cm_yc, reason = api.device_get_yc("cm")
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            context['cm_yc'] = cm_yc
    # 获取项目绑定环境箱设备信息
    status, bd_ec_list, reason = api.project_get_device_by_type(prj_id, "ec")
    if status != api.OK:
        ec_sign = {"绑定ec设备状态": "没绑定"}
        context['ec_sign'] = ec_sign
    else:
        ec_sign = {"绑定ec设备状态": "绑定"}
        context['ec_sign'] = ec_sign
        # 获取环境箱设备遥信数据
        status, ec_yx, reason = api.device_get_yx("ec")
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            context['ec_yx'] = ec_yx
        # 获取环境箱设备遥测数据
        status, ec_yc, reason = api.device_get_yc("ec")
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            context['ec_yc'] = ec_yc
    # 获取项目绑定充放电机设备信息
    status, bd_cd_list, reason = api.project_get_device_by_type(prj_id, "cd")
    if status != api.OK:
        cd_sign = {"绑定cd设备状态": "没绑定"}
        context['cd_sign'] = cd_sign
    else:
        cd_sign = {"绑定cd设备状态": "绑定"}
        context['cd_sign'] = cd_sign
        # 获取充放电机设备遥信数据
        status, cd_yx, reason = api.device_get_yx("cd")
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            context['cd_yx'] = cd_yx
        # 获取充放电机设备遥测数据
        status, cd_yc, reason = api.device_get_yc("cd")
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            context['cd_yc'] = cd_yc
    # 获取项目绑定BMS设备信息
    status, bd_bms_list, reason = api.project_get_device_by_type(prj_id, "bms")
    if status != api.OK:
        bms_sign = {"绑定bms设备状态": "没绑定"}
        context['bms_sign'] = bms_sign
    else:
        bms_sign = {"绑定bms设备状态": "绑定"}
        context['bms_sign'] = bms_sign
        # 获取BMS设备遥信数据
        status, bms_yx, reason = api.device_get_yx("bms")
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            context['bms_yx'] = bms_yx
        # 获取BMS设备遥测数据
        status, bms_yc, reason = api.device_get_yc("bms")
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            context['bms_yc'] = bms_yc

    # 渲染页面
    return render(request, "10-项目页面/36-设备信息摘要页面/equipment_information.html", context=context)

urlpatterns = [
    path('summary/<int:prj_id>/', show_project_device_summary, name='显示项目关联设备概要')
]
urls= (urlpatterns, 'plane', 'plane')


