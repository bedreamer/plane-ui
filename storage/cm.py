from django.urls import path
from django.shortcuts import render
import api as api

from django.urls import path, include, reverse
from django.shortcuts import render
from django.http import *
from storage.models import *
import api as api
import os
import storage.views_plane as plane

dev_type = 'cm'

def get_CM_device_pair_information():
    info = ["01-水冷机页面"]
    status, pr, reason = api.device_get_profile(dev_type)
    if status != api.OK:
        return api.return_error_payload(info)
    info.append(pr['vendor'])
    info.append(pr['model'])
    info.append(pr['version'])

    return api.return_ok_payload(info)


# Create your views here.
def show_CM_yc_page(request):
    context = dict()


    # 获取整在执行项目的项目ID
    status, zx_list, reason = api.project_list_running()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "读取配置参数错误")
    else:
        xm_id = zx_list[0].id
    # 查看水冷机驱动是否开启
    status, xm_fwzt_list, reason = api.project_service_status(xm_id)
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "未通讯/或sid错误")
    else:
        for xm_fwzt in xm_fwzt_list:
            for i in xm_fwzt.keys():
                if i == "dev_type":
                    if xm_fwzt[i] == "cm":
                        for i in xm_fwzt.keys():
                            if i == "服务中":
                                cm_zt = xm_fwzt[i]
                                cm_qd_zt = {"驱动状态": cm_zt}
                                context['cm_qd_zt'] = cm_qd_zt
    if cm_zt != False:
        #获取路径
        status, path_pair, reason = get_CM_device_pair_information()
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "读取配置参数错误")

        path_pair.append('cm_yaoce.html')
        path = '/'.join(path_pair)
        #获取水冷机遥测信息
        status, cm_yc, reason = api.device_get_yc(dev_type)
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            #return render(request, "未通讯/或sid错误")

        context['cm_yc'] = cm_yc              #下发遥信数据
        return render(request, path, context=context)
        #return render(request, "01-水冷机页面/newline/HL-160/V1.0/cm_yaoce.html", context=context)
    else:
        return render(request, "01-水冷机页面/newline/HL-160/V1.0/cm_qudong_xinxi.html", context=context)

def show_CM_yx_page(request):
    context = dict()
    #获取整在执行项目的项目ID
    status, zx_list, reason = api.project_list_running()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "读取配置参数错误")
    else:
        xm_id = zx_list[0].id
    #查看水冷机驱动是否开启
    status, xm_fwzt_list, reason = api.project_service_status(xm_id)
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "未通讯/或sid错误")
    else:
        for xm_fwzt in xm_fwzt_list:
            for i in xm_fwzt.keys():
                if i == "dev_type":
                    if xm_fwzt[i] == "cm":
                        for i in xm_fwzt.keys():
                            if i == "服务中":
                                cm_zt = xm_fwzt[i]
                                cm_qd_zt = {"驱动状态": cm_zt}
                                context['cm_qd_zt'] = cm_qd_zt
    if cm_zt != False:
        #获取路径
        status, path_pair, reason = get_CM_device_pair_information()
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "读取配置参数错误")

        path_pair.append('cm_yaoce.html')
        path = '/'.join(path_pair)
        # 获取水冷机遥信信息
        status, cm_yx, reason = api.device_get_yx(dev_type)
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")

        context['cm_yx'] = cm_yx
        return render(request, path, context=context)
        # return render(request, "01-水冷机页面/newline/HL-160/V1.0/cm_yaoxin.html", context=context)
    else:
        return render(request, "01-水冷机页面/newline/HL-160/V1.0/cm_qudong_xinxi.html", context=context)


def show_CM_yt_page(request):
    context = dict()
    if request.method == 'GET':
        # 获取整在执行项目的项目ID
        status, zx_list, reason = api.project_list_running()
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "读取配置参数错误")
        else:
            xm_id = zx_list[0].id
        # 查看水冷机驱动是否开启
        status, xm_fwzt_list, reason = api.project_service_status(xm_id)
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            for xm_fwzt in xm_fwzt_list:
                for i in xm_fwzt.keys():
                    if i == "dev_type":
                        if xm_fwzt[i] == "cm":
                            for i in xm_fwzt.keys():
                                if i == "服务中":
                                    cm_zt = xm_fwzt[i]
                                    cm_qd_zt = {"驱动状态": cm_zt}
                                    context['cm_qd_zt'] = cm_qd_zt
        if cm_zt != False:
            #status, path_pair, reason = get_CM_device_pair_information()
            #if status != api.OK:
            #    reason = {"错误原因": reason}
            #    context['reason'] = reason
            #    return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
                #return render(request, "读取配置参数错误")

            #path_pair.append('cm_yaotiao.html')
            #path = '/'.join(path_pair)
            path = "01-水冷机页面/newline/HL-160/V1.0/cm_yaotiao.html"       #临时

            #status1, cm_yt, reason1 = api.device_get_yt(dev_type)
            status1, cm_yt, reason1 = api.project_list()                          #临时
            if status1 != api.OK:
                reason ={ "错误原因":reason1 }
                context['reason'] = reason
                return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
                #return render(request, "未通讯/或sid错误")
            else:
                context['cm_yt'] = cm_yt
                return render(request, path, context=context)
        else:
            return render(request, "01-水冷机页面/newline/HL-160/V1.0/cm_qudong_xinxi.html", context=context)
    else:
        # 获取页面新值
        temperature_value = request.POST.get("温度值")
        flow_value = request.POST.get("流量值")
        execution_time = request.POST.get("执行时间")
        heating_percentage = request.POST.get("加热百分比")
        average_battery_temperature = request.POST.get("电池平均温度")
        maximum_battery_voltage = request.POST.get("最高电池温度")
        minimum_battery_voltage = request.POST.get("最低电池温度")
        battery_voltage = request.POST.get("电池电压")
        # 获取服务器老值
        #status, yt, reason = api.device_get_yt(dev_type)
        status, yt, reason = api.project_list()  # 临时
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            #temperature_value1 = yt.温度
            temperature_value1 = "10"
            #flow_value1 = yt.流量
            flow_value1 = "10"
            #execution_time1 = yt.执行时间
            execution_time1 = "10"
            #heating_percentage1 = yt.加热百分比
            heating_percentage1 = "10"
            #average_battery_temperature1 = yt.电池平均温度
            average_battery_temperature1 = "10"
            #maximum_battery_voltage1 = yt.最高电池温度
            maximum_battery_voltage1 = "10"
            #minimum_battery_voltage1 = yt.最低电池温度
            minimum_battery_voltage1 = "10"
            #battery_voltage1 = yt.电池电压
            battery_voltage1 = "10"

            if temperature_value != temperature_value1 or \
                    flow_value != flow_value1 or \
                    execution_time != execution_time1 or \
                    heating_percentage != heating_percentage1 or \
                    average_battery_temperature != average_battery_temperature1 or \
                    maximum_battery_voltage != maximum_battery_voltage1 or \
                    minimum_battery_voltage != minimum_battery_voltage1 or \
                    battery_voltage != battery_voltage1:
                price = 2  # 只要有一个不同就标志位置1
            else:
                price = 1  # 都是相同就标志位置0
            if price == 2:
                if temperature_value != temperature_value1:
                    status, project_list, reason = api.device_set_yt(dev_type, "温度", temperature_value)  # 下发遥调信息
                    #status, pz_list, reason = api.project_list_configure()
                    if status != api.OK:  # 下发失败，渲染遥调失败页面
                        #status1, path_pair, reason1 = get_CM_device_pair_information()  # 获取遥调失败页面路径
                        #if status1 != api.OK:  # 获取遥调失败页面路径失败，渲染报错页面
                        #    return render(request, "07-告警提示页面/alarm_prompt.html")
                            # return render(request, "读取配置参数错误")
                        #else:
                        #    path_pair.append('cm_yt_sb.html')
                        #    path = '/'.join(path_pair)
                        #    skip = {"数据点": "温度", "有无遥调值变化": "有", "错误原因": reason}
                        #    context['skip'] = skip
                        #    return render(request, path, context=context)
                        try:
                            next_url = request.GET['next']
                        except KeyError:
                            next_url = reverse('cm设备遥调失败页面', args=("温度", "有", reason))
                        return HttpResponseRedirect(next_url)

                if flow_value != flow_value1:
                    status, project_list, reason = api.device_set_yt(dev_type, "流量", flow_value)  # 下发遥调信息
                    # status, pz_list, reason = api.project_list_configure()
                    if status != api.OK:
                        #status1, path_pair, reason1 = get_CM_device_pair_information()
                        #if status1 != api.OK:
                        #    return render(request, "07-告警提示页面/alarm_prompt.html")
                            # return render(request, "读取配置参数错误")
                        #else:
                        #    path_pair.append('cm_yt_sb.html')
                        #    path = '/'.join(path_pair)
                        #    skip = {"数据点": "流量", "有无遥调值变化": "有", "错误原因": reason}
                        #    context['skip'] = skip
                        #    return render(request, path, context=context)
                        try:
                            next_url = request.GET['next']
                        except KeyError:
                            next_url = reverse('cm设备遥调失败页面', args=("流量", "有", reason))
                        return HttpResponseRedirect(next_url)

                if execution_time != execution_time1:
                    status, project_list, reason = api.device_set_yt(dev_type, "执行时间", execution_time)  # 下发遥调信息
                    # status, pz_list, reason = api.project_list_configure()
                    if status != api.OK:
                        #status1, path_pair, reason1 = get_CM_device_pair_information()
                        #if status1 != api.OK:
                        #    return render(request, "07-告警提示页面/alarm_prompt.html")
                            # return render(request, "读取配置参数错误")
                        #else:
                        #    path_pair.append('cm_yt_sb.html')
                        #    path = '/'.join(path_pair)
                        #    skip = {"数据点": "执行时间", "有无遥调值变化": "有", "错误原因": reason}
                        #    context['skip'] = skip
                        #    return render(request, path, context=context)
                        try:
                            next_url = request.GET['next']
                        except KeyError:
                            next_url = reverse('cm设备遥调失败页面', args=("执行时间", "有", reason))
                        return HttpResponseRedirect(next_url)


                if heating_percentage != heating_percentage1:
                    status, project_list, reason = api.device_set_yt(dev_type, "加热百分比", heating_percentage)  # 下发遥调信息
                    # status, pz_list, reason = api.project_list_configure()
                    if status != api.OK:
                        #status1, path_pair, reason1 = get_CM_device_pair_information()
                        #if status1 != api.OK:
                        #    return render(request, "07-告警提示页面/alarm_prompt.html")
                            # return render(request, "读取配置参数错误")
                        #else:
                        #    path_pair.append('cm_yt_sb.html')
                        #    path = '/'.join(path_pair)
                        #    skip = {"数据点": "加热百分比", "有无遥调值变化": "有", "错误原因": reason}
                        #    context['skip'] = skip
                        #    return render(request, path, context=context)
                        try:
                            next_url = request.GET['next']
                        except KeyError:
                            next_url = reverse('cm设备遥调失败页面', args=("加热百分比", "有", reason))
                        return HttpResponseRedirect(next_url)

                if average_battery_temperature != average_battery_temperature1:
                    status, project_list, reason = api.device_set_yt(dev_type, "电池平均温度", average_battery_temperature)  # 下发遥调信息
                    # status, pz_list, reason = api.project_list_configure()
                    if status != api.OK:
                        #status1, path_pair, reason1 = get_CM_device_pair_information()
                        #if status1 != api.OK:
                        #    return render(request, "07-告警提示页面/alarm_prompt.html")
                            # return render(request, "读取配置参数错误")
                        #else:
                        #    path_pair.append('cm_yt_sb.html')
                        #    path = '/'.join(path_pair)
                        #    skip = {"数据点": "电池平均温度", "有无遥调值变化": "有", "错误原因": reason}
                        #    context['skip'] = skip
                        #    return render(request, path, context=context)
                        try:
                            next_url = request.GET['next']
                        except KeyError:
                            next_url = reverse('cm设备遥调失败页面', args=("电池平均温度", "有", reason))
                        return HttpResponseRedirect(next_url)

                if maximum_battery_voltage != maximum_battery_voltage1:
                    status, project_list, reason = api.device_set_yt(dev_type, "最高电池温度", maximum_battery_voltage)  # 下发遥调信息
                    # status, pz_list, reason = api.project_list_configure()
                    if status != api.OK:
                        #status1, path_pair, reason1 = get_CM_device_pair_information()
                        #if status1 != api.OK:
                        #    return render(request, "07-告警提示页面/alarm_prompt.html")
                            # return render(request, "读取配置参数错误")
                        #else:
                        #    path_pair.append('cm_yt_sb.html')
                        #    path = '/'.join(path_pair)
                        #    skip = {"数据点": "最高电池温度", "有无遥调值变化": "有", "错误原因": reason}
                        #    context['skip'] = skip
                        #    return render(request, path, context=context)
                        try:
                            next_url = request.GET['next']
                        except KeyError:
                            next_url = reverse('cm设备遥调失败页面', args=("最高电池温度", "有", reason))
                        return HttpResponseRedirect(next_url)

                if minimum_battery_voltage != minimum_battery_voltage1:
                    status, project_list, reason = api.device_set_yt(dev_type, "最低电池温度", minimum_battery_voltage)  # 下发遥调信息
                    # status, pz_list, reason = api.project_list_configure()
                    if status != api.OK:
                        #status1, path_pair, reason1 = get_CM_device_pair_information()
                        #if status1 != api.OK:
                        #    return render(request, "07-告警提示页面/alarm_prompt.html")
                            # return render(request, "读取配置参数错误")
                        #else:
                        #    path_pair.append('cm_yt_sb.html')
                        #    path = '/'.join(path_pair)
                        #    skip = {"数据点": "最低电池温度", "有无遥调值变化": "有", "错误原因": reason}
                        #    context['skip'] = skip
                        #    return render(request, path, context=context)
                        try:
                            next_url = request.GET['next']
                        except KeyError:
                            next_url = reverse('cm设备遥调失败页面', args=("最低电池温度", "有", reason))
                        return HttpResponseRedirect(next_url)

                if battery_voltage != battery_voltage1:
                    status, project_list, reason = api.device_set_yt(dev_type, "电池电压", battery_voltage)  # 下发遥调信息
                    # status, pz_list, reason = api.project_list_configure()
                    if status != api.OK:
                        #status1, path_pair, reason1 = get_CM_device_pair_information()
                        #if status1 != api.OK:
                        #    return render(request, "07-告警提示页面/alarm_prompt.html")
                            # return render(request, "读取配置参数错误")
                        #else:
                        #    path_pair.append('cm_yt_sb.html')
                        #    path = '/'.join(path_pair)
                        #    skip = {"数据点": "电池电压", "有无遥调值变化": "有", "错误原因": reason}
                        #    context['skip'] = skip
                        #    return render(request, path, context=context)
                        try:
                            next_url = request.GET['next']
                        except KeyError:
                            next_url = reverse('cm设备遥调失败页面', args=("电池电压", "有", reason))
                        return HttpResponseRedirect(next_url)

                # 进这里说明一定是有遥调变化 ，把变化的都下发成功，总的提示一个成功即可
                try:
                    next_url = request.GET['next']
                except KeyError:
                    next_url = reverse('cm设备遥调成功页面', args=("", ""))
                return HttpResponseRedirect(next_url)
            #一个都没有变化
            elif price == 1:
                #status1, path_pair, reason = get_CM_device_pair_information()
                #if status1 != api.OK:
                #    return render(request, "07-告警提示页面/alarm_prompt.html")
                    # return render(request, "读取配置参数错误")
                #else:
                #    path_pair.append('cm_yt_sb.html')
                #    path = '/'.join(path_pair)
                #    skip = {"有无遥调值变化": "无", "错误原因": "配置的遥调数据无变化"}
                #    context['skip'] = skip
                #    return render(request, path, context=context)
                try:
                    next_url = request.GET['next']
                except KeyError:
                    next_url = reverse('cm设备遥调失败页面', args=("无","无", "配置的遥调数据无变化"))
                return HttpResponseRedirect(next_url)


def show_CM_yk_page(request):
    context = dict()
    if request.method == 'GET':
        # 获取整在执行项目的项目ID
        status, zx_list, reason = api.project_list_running()
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "读取配置参数错误")
        else:
            xm_id = zx_list[0].id
        # 查看水冷机驱动是否开启
        status, xm_fwzt_list, reason = api.project_service_status(xm_id)
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "未通讯/或sid错误")
        else:
            for xm_fwzt in xm_fwzt_list:
                for i in xm_fwzt.keys():
                    if i == "dev_type":
                        if xm_fwzt[i] == "cm":
                            for i in xm_fwzt.keys():
                                if i == "服务中":
                                    cm_zt = xm_fwzt[i]
                                    cm_qd_zt = {"驱动状态": cm_zt}
                                    context['cm_qd_zt'] = cm_qd_zt
        if cm_zt != False:
            #status, path_pair, reason = get_CM_device_pair_information()
            #if status != api.OK:
            #    reason = {"错误原因": reason}
            #    context['reason'] = reason
            #    return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
                #return render(request, "读取配置参数错误")

            #path_pair.append('cm_yaokong.html')
            #path = '/'.join(path_pair)

            path = "01-水冷机页面/newline/HL-160/V1.0/cm_yaokong.html"  # 临时

            #status1, cm_yk, reason1 = api.device_get_yk(dev_type)
            status1, cm_yk, reason1 = api.project_list()  # 临时
            if status1 != api.OK:
                reason = {"错误原因": reason1}
                context['reason'] = reason
                return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
                #return render(request, "未通讯/或sid错误")

            context['cm_yk'] = cm_yk
            return render(request, path, context=context)
        else:
            return render(request, "01-水冷机页面/newline/HL-160/V1.0/cm_qudong_xinxi.html", context=context)
    else:
        heater_running_state_dk = request.POST.get("加热器运行状态_打开")
        heater_running_state_gb = request.POST.get("加热器运行状态_关闭")
        compressor_running_state_dk = request.POST.get("压缩机运行状态_断开")
        compressor_running_state_bh = request.POST.get("压缩机运行状态_闭合")
        circulating_running_state_dk = request.POST.get("循环泵运行状态_打开")
        circulating_running_state_gb = request.POST.get("循环泵运行状态_关闭")
        permissible_state_heating_dk = request.POST.get("加热允许状态_断开")
        permissible_state_heating_bh = request.POST.get("加热允许状态_闭合")
        permissible_state_refrigeration_dk = request.POST.get("制冷允许状态_打开")
        permissible_state_refrigeration_gb = request.POST.get("制冷允许状态_关闭")
        coolant_stock_status_dk = request.POST.get("冷却液存量状态_断开")
        coolant_stock_status_gb = request.POST.get("冷却液存量状态_闭合")

        key = "加热器运行状态"
        if heater_running_state_dk != None:
            key = "加热器运行状态"
            value = heater_running_state_dk
        elif heater_running_state_gb != None:
            key = "加热器运行状态"
            value = heater_running_state_gb
        elif compressor_running_state_dk != None:
            key = "压缩机运行状态"
            value = compressor_running_state_dk
        elif compressor_running_state_bh != None:
            key = "压缩机运行状态"
            value = compressor_running_state_bh
        elif circulating_running_state_dk != None:
            key = "循环泵运行状态"
            value = circulating_running_state_dk
        elif circulating_running_state_gb != None:
            key = "循环泵运行状态"
            value = circulating_running_state_gb
        elif permissible_state_heating_dk != None:
            key = "加热允许状态"
            value = permissible_state_heating_dk
        elif permissible_state_heating_bh != None:
            key = "加热允许状态"
            value = permissible_state_heating_bh
        elif permissible_state_refrigeration_dk != None:
            key = "制冷允许状态"
            value = permissible_state_refrigeration_dk
        elif permissible_state_refrigeration_gb != None:
            key = "制冷允许状态"
            value = permissible_state_refrigeration_gb
        elif coolant_stock_status_dk != None:
            key = "冷却液存量状态"
            value = coolant_stock_status_dk
        elif coolant_stock_status_gb != None:
            key = "冷却液存量状态"
            value = coolant_stock_status_gb

        # status, project_list, reason = api.device_set_yk(dev_type, key, value)  # 下发遥控信息
        status, pz_list, reason = api.project_list_configure()  # 临时
        status = "no"
        if status != api.OK:
            #status1, path_pair, reason1 = get_CM_device_pair_information()
            #if status1 != api.OK:
            #    return render(request, "07-告警提示页面/alarm_prompt.html")
                # return render(request, "读取配置参数错误")
            #else:
            #    path_pair.append('cm_yk_sb.html')
            #    path = '/'.join(path_pair)
            #    skip = {"配置状态": "error", "错误原因": reason, "数据点": key}
            #    context['skip'] = skip

            try:
                next_url = request.GET['next']
            except KeyError:
                next_url = reverse('cm设备遥控失败页面', args=(key,reason,"error"))
            return HttpResponseRedirect(next_url)
            #return render(request, path, context=context)
        else:
            #status1, path_pair, reason1 = get_CM_device_pair_information()
            #if status1 != api.OK:
            #    return render(request, "07-告警提示页面/alarm_prompt.html")
                # return render(request, "读取配置参数错误")
            #else:
                #path_pair.append('cm_yk_cg.html')
                #path = '/'.join(path_pair)
                #skip = {"配置状态": "ok", "数据点": key}
                #context['skip'] = skip

            try:
                next_url = request.GET['next']
            except KeyError:
                next_url = reverse('cm设备遥控成功页面', args=(key,"ok"))
            return HttpResponseRedirect(next_url)
            #return render(request, path, context=context)


def cm_yt_cg_page(request, prj_data, prj_change):
    context = dict()
    status, path_pair, reason = get_CM_device_pair_information()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "读取配置参数错误")
    else:
        path_pair.append('cm_yt_cg.html')
        path = '/'.join(path_pair)
        return render(request, path, context=context)


def cm_yt_sb_page(request, prj_data, prj_change, prj_reason):
    context = dict()
    status, path_pair, reason = get_CM_device_pair_information()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "读取配置参数错误")
    else:
        path_pair.append('cm_yt_sb.html')
        path = '/'.join(path_pair)
        skip = {"数据点":prj_data,"有无遥调值变化": prj_change, "错误原因": prj_reason}
        context['skip'] = skip
        return render(request, path, context=context)


def cm_yk_cg_page(request, prj_key, prj_state):
    context = dict()
    status, path_pair, reason = get_CM_device_pair_information()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "读取配置参数错误")
    else:
        path_pair.append('cm_yk_cg.html')
        path = '/'.join(path_pair)
        skip = { "配置状态":"ok", "数据点": prj_key}
        context['skip'] = skip
        return render(request, path, context=context)


def cm_yk_sb_page(request,prj_key,prj_state,prj_reason):
    context = dict()
    status, path_pair, reason = get_CM_device_pair_information()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "读取配置参数错误")
    else:
        path_pair.append('cm_yk_sb.html')
        path = '/'.join(path_pair)
        skip = {"配置状态": "error", "错误原因": prj_reason, "数据点": prj_key}
        context['skip'] = skip
        return render(request, path, context=context)


urlpatterns = [
    path('cm/yc/', show_CM_yc_page, name="cm yc page"),
    path('cm/yx/', show_CM_yx_page, name="cm yx page"),
    path('cm/yt/', show_CM_yt_page, name="cm yt page"),
    path('cm/yk/', show_CM_yk_page, name="cm yk page"),
    path('<str:prj_data>/cm/yt/success/<str:prj_change>/', cm_yt_cg_page, name="cm设备遥调成功页面"),
    path('<str:prj_data>/cm/yt/fail/<str:prj_change>/<str:prj_reason>/', cm_yt_sb_page, name="cm设备遥调失败页面"),
    path('<str:prj_key>/cm/yk/success/<str:prj_state>', cm_yk_cg_page, name="cm设备遥控成功页面"),
    path('<str:prj_key>/cm/yk/fail/<str:prj_state>/<str:prj_reason>/', cm_yk_sb_page, name="cm设备遥控失败页面"),
]
urls= (urlpatterns, 'cm', 'cm' )

