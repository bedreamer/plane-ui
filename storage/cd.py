from django.urls import path
from django.shortcuts import render
import api as api

dev_type = 'cd'

def get_CD_device_pair_information():
    info = ["03-充放电机页面"]
    status, pr, reason = api.device_get_profile(dev_type)
    if status != api.OK:
        return api.return_error_payload(info)
    info.append(pr['vendor'])
    info.append(pr['model'])
    info.append(pr['version'])

    return api.return_ok_payload(info)


# Create your views here.
def show_CD_yc_page(request):
    status, path_pair, reason = get_CD_device_pair_information()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        #return render(request, "读取配置参数错误")

    path_pair.append('cd_yaoce.html')
    path = '/'.join(path_pair)

    context = dict()
    status, cd_yc, reason = api.device_get_yc(dev_type)
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        #return render(request, "未通讯/或sid错误")

    context['cd_yc'] = cd_yc
    return render(request, path, context=context)


def show_CD_yx_page(request):
    status, path_pair, reason = get_CD_device_pair_information()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        #return render(request, "读取配置参数错误")

    path_pair.append('cd_yaoxin.html')
    path = '/'.join(path_pair)

    context = dict()
    status, cd_yx, reason = api.device_get_yx(dev_type)
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        #return render(request, "未通讯/或sid错误")

    context['cd_yx'] = cd_yx
    return render(request, path, context=context)


def show_CD_yt_page(request):
    context = dict()
    status, path_pair, reason = get_CD_device_pair_information()
    if status != api.OK:
        reason = {"错误原因": reason}
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        #return render(request, "读取配置参数错误")

    path_pair.append('cd_yaotiao.html')
    path = '/'.join(path_pair)

    status1, cd_yt, reason1 = api.device_get_yt(dev_type)
    if status1 != api.OK:
        reason = {"错误原因": reason1}
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        #return render(request, "未通讯/或sid错误")

    context['cd_yt'] = cd_yt
    return render(request, path, context=context)


def show_CD_yk_page(request):
    context = dict()
    status, path_pair, reason = get_CD_device_pair_information()
    if status != api.OK:
        reason = {"错误原因": reason}
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        #return render(request, "读取配置参数错误")

    path_pair.append('cd_yaokong.html')
    path = '/'.join(path_pair)

    status1, cd_yk, reason1 = api.device_get_yk(dev_type)
    if status1 != api.OK:
        reason = {"错误原因": reason1}
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        #return render(request, "未通讯/或sid错误")

    context['cd_yk'] = cd_yk
    return render(request, path, context=context)


def cd_yt_cg_page(request):         #把新数据从上面拿下来，再从表里拿到原来的值，比较，不同下发，相同不发
    context = dict()
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
    status, yt, reason = api.device_get_yt(dev_type)
    # status, yt, reason = api.project_list()  # 临时
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "未通讯/或sid错误")
    else:
        temperature_value1 = yt.温度
        flow_value1 = yt.流量
        execution_time1 = yt.执行时间
        heating_percentage1 = yt.加热百分比
        average_battery_temperature1 = yt.电池平均温度
        maximum_battery_voltage1 = yt.最高电池温度
        minimum_battery_voltage1 = yt.最低电池温度
        battery_voltage1 = yt.电池电压

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
            # status, pz_list, reason = api.project_list_configure()
            if status != api.OK:  # 下发失败，渲染遥调失败页面
                status1, path_pair, reason1 = get_CD_device_pair_information()  # 获取遥调失败页面路径
                if status1 != api.OK:  # 获取遥调失败页面路径失败，渲染报错页面
                    return render(request, "07-告警提示页面/alarm_prompt.html")
                    # return render(request, "读取配置参数错误")
                else:
                    path_pair.append('ec_yt_sb.html')
                    path = '/'.join(path_pair)
                    skip = {"数据点": "温度", "有无遥调值变化": "有", "错误原因": reason}
                    context['skip'] = skip
                    return render(request, path, context=context)

        if flow_value != flow_value1:
            status, project_list, reason = api.device_set_yt(dev_type, "流量", flow_value)  # 下发遥调信息
            # status, pz_list, reason = api.project_list_configure()
            if status != api.OK:
                status1, path_pair, reason1 = get_CD_device_pair_information()
                if status1 != api.OK:
                    return render(request, "07-告警提示页面/alarm_prompt.html")
                    # return render(request, "读取配置参数错误")
                else:
                    path_pair.append('ec_yt_sb.html')
                    path = '/'.join(path_pair)
                    skip = {"数据点": "流量", "有无遥调值变化": "有", "错误原因": reason}
                    context['skip'] = skip
                    return render(request, path, context=context)

        if execution_time != execution_time1:
            status, project_list, reason = api.device_set_yt(dev_type, "执行时间", execution_time)  # 下发遥调信息
            # status, pz_list, reason = api.project_list_configure()
            if status != api.OK:
                status1, path_pair, reason1 = get_CD_device_pair_information()
                if status1 != api.OK:
                    return render(request, "07-告警提示页面/alarm_prompt.html")
                    # return render(request, "读取配置参数错误")
                else:
                    path_pair.append('ec_yt_sb.html')
                    path = '/'.join(path_pair)
                    skip = {"数据点": "执行时间", "有无遥调值变化": "有", "错误原因": reason}
                    context['skip'] = skip
                    return render(request, path, context=context)

        if heating_percentage != heating_percentage1:
            status, project_list, reason = api.device_set_yt(dev_type, "加热百分比", heating_percentage)  # 下发遥调信息
            # status, pz_list, reason = api.project_list_configure()
            if status != api.OK:
                status1, path_pair, reason1 = get_CD_device_pair_information()
                if status1 != api.OK:
                    return render(request, "07-告警提示页面/alarm_prompt.html")
                    # return render(request, "读取配置参数错误")
                else:
                    path_pair.append('ec_yt_sb.html')
                    path = '/'.join(path_pair)
                    skip = {"数据点": "加热百分比", "有无遥调值变化": "有", "错误原因": reason}
                    context['skip'] = skip
                    return render(request, path, context=context)

        if average_battery_temperature != average_battery_temperature1:
            status, project_list, reason = api.device_set_yt(dev_type, "电池平均温度", average_battery_temperature)  # 下发遥调信息
            # status, pz_list, reason = api.project_list_configure()
            if status != api.OK:
                status1, path_pair, reason1 = get_CD_device_pair_information()
                if status1 != api.OK:
                    return render(request, "07-告警提示页面/alarm_prompt.html")
                    # return render(request, "读取配置参数错误")
                else:
                    path_pair.append('ec_yt_sb.html')
                    path = '/'.join(path_pair)
                    skip = {"数据点": "电池平均温度", "有无遥调值变化": "有", "错误原因": reason}
                    context['skip'] = skip
                    return render(request, path, context=context)

        if maximum_battery_voltage != maximum_battery_voltage1:
            status, project_list, reason = api.device_set_yt(dev_type, "最高电池温度", maximum_battery_voltage)  # 下发遥调信息
            # status, pz_list, reason = api.project_list_configure()
            if status != api.OK:
                status1, path_pair, reason1 = get_CD_device_pair_information()
                if status1 != api.OK:
                    return render(request, "07-告警提示页面/alarm_prompt.html")
                    # return render(request, "读取配置参数错误")
                else:
                    path_pair.append('cm_yt_sb.html')
                    path = '/'.join(path_pair)
                    skip = {"数据点": "最高电池温度", "有无遥调值变化": "有", "错误原因": reason}
                    context['skip'] = skip
                    return render(request, path, context=context)

        if minimum_battery_voltage != minimum_battery_voltage1:
            status, project_list, reason = api.device_set_yt(dev_type, "最低电池温度", minimum_battery_voltage)  # 下发遥调信息
            # status, pz_list, reason = api.project_list_configure()
            if status != api.OK:
                status1, path_pair, reason1 = get_CD_device_pair_information()
                if status1 != api.OK:
                    return render(request, "07-告警提示页面/alarm_prompt.html")
                    # return render(request, "读取配置参数错误")
                else:
                    path_pair.append('cm_yt_sb.html')
                    path = '/'.join(path_pair)
                    skip = {"数据点": "最低电池温度", "有无遥调值变化": "有", "错误原因": reason}
                    context['skip'] = skip
                    return render(request, path, context=context)

        if battery_voltage != battery_voltage1:
            status, project_list, reason = api.device_set_yt(dev_type, "电池电压", battery_voltage)  # 下发遥调信息
            # status, pz_list, reason = api.project_list_configure()
            if status != api.OK:
                status1, path_pair, reason1 = get_CD_device_pair_information()
                if status1 != api.OK:
                    return render(request, "07-告警提示页面/alarm_prompt.html")
                    # return render(request, "读取配置参数错误")
                else:
                    path_pair.append('cm_yt_sb.html')
                    path = '/'.join(path_pair)
                    skip = {"数据点": "电池电压", "有无遥调值变化": "有", "错误原因": reason}
                    context['skip'] = skip
                    return render(request, path, context=context)

        # 进这里说明一定是有遥调变化 ，把变化的都下发成功，总的提示一个成功即可
        status1, path_pair, reason1 = get_CD_device_pair_information()
        if status1 != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "读取配置参数错误")
        path_pair.append('ec_yt_cg.html')
        path = '/'.join(path_pair)
        return render(request, path, context=context)
    elif price == 1:
        status1, path_pair, reason1 = get_CD_device_pair_information()
        if status1 != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "读取配置参数错误")
        else:
            path_pair.append('ec_yt_sb.html')
            path = '/'.join(path_pair)
            skip = {"有无遥调值变化": "无", "错误原因": "配置的遥调数据无变化"}
            context['skip'] = skip
            return render(request, path, context=context)


def cd_yt_sb_page(request):
    context = dict()
    status, path_pair, reason = get_CD_device_pair_information()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "读取配置参数错误")
    else:
        path_pair.append('cd_yt_sb.html')
        path = '/'.join(path_pair)
        return render(request, path, context=context)


def cd_yk_cg_page(request):
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

    status, project_list, reason = api.device_set_yk(dev_type, key, value)  # 下发遥控信息
    # status, pz_list, reason = api.project_list_configure()
    context = dict()
    if status != api.OK:
        status1, path_pair, reason1 = get_CD_device_pair_information()
        if status1 != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "读取配置参数错误")
        else:
            path_pair.append('ec_yk_sb.html')
            path = '/'.join(path_pair)
            skip = {"错误原因": reason, "数据点": key}
            context['skip'] = skip
            return render(request, path, context=context)
    else:
        status1, path_pair, reason1 = get_CD_device_pair_information()
        if status1 != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html")
            # return render(request, "读取配置参数错误")
        else:
            path_pair.append('ec_yk_cg.html')
            path = '/'.join(path_pair)
            skip = {"数据点": key}
            context['skip'] = skip
            return render(request, path, context=context)


def cd_yk_sb_page(request):
    context = dict()
    status, path_pair, reason = get_CD_device_pair_information()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "读取配置参数错误")
    else:
        path_pair.append('cd_yk_sb.html')
        path = '/'.join(path_pair)
        return render(request, path, context=context)

urlpatterns = [
    path('cd/yc/', show_CD_yc_page, name="cd yc page"),
    path('cd/yx/', show_CD_yx_page, name="cd yx page"),
    path('cd/yt/', show_CD_yt_page, name="cd yt page"),
    path('cd/yk/', show_CD_yk_page, name="cd yk page"),
    path('cd/yt/success/', cd_yt_cg_page, name="cd设备遥调成功页面"),
    path('cd/yt/fail/', cd_yt_sb_page, name="cd设备遥调失败页面"),
    path('cd/yk/success/', cd_yk_cg_page, name="cd设备遥控成功页面"),
    path('cd/yk/fail/', cd_yk_sb_page, name="cd设备遥控失败页面"),
]
urls= (urlpatterns, 'cd', 'cd' )
