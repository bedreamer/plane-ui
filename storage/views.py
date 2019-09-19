from django.urls import path, include
from django.shortcuts import render
import api as api
import os


def home_page_page(request):
    context = dict()
    return render(request, '10-项目页面/01-系统首页/home_page.html', context=context)


#暂停原因输入页面
def suspend_project_cause_page(request, prj_id):
    context = dict()
    status, xm_list, reason = api.project_get(prj_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        # 拿到绑定的充放电机设备ID信息
        xm_name = xm_list.name

    ID = {"项目ID": prj_id, "项目名": xm_name}
    context['ID'] = ID
    return render(request, '10-项目页面/10-暂停项目原因输入页面/suspend_project_cause.html', context=context)


#暂停成功页面
def successful_suspension_project_page(request):
    context = dict()
    xm_id = request.POST.get("xm_id")
    ztyy = request.POST.get("ztyy")
    status, xm_list, reason = api.project_get(xm_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        xm_name = xm_list.name

    status1, project_list, reason1 = api.project_service_stop()  # 暂停项目
    #status1 = "是ok"
    if status1 != api.OK:
        ID = { "项目名":xm_name,"错误原因":reason1 }
        context['ID'] = ID
        return render(request, '10-项目页面/21-暂停项目失败页面/project_suspension_failed.html', context=context)
    else:
        ID = { "项目名": xm_name }
        context['ID'] = ID
        return render(request, '10-项目页面/20-暂停项目成功页面/successful_suspension_project.html', context=context)


def project_suspension_failed_page(request):
    context = dict()
    return render(request, '10-项目页面/21-暂停项目失败页面/project_suspension_failed.html', context=context)


#中止原因输入页面
def cease_project_cause_page(request, prj_id):
    context = dict()
    status, xm_list, reason = api.project_get(prj_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        # 拿到绑定的充放电机设备ID信息
        xm_name = xm_list.name

    ID = {"项目ID": prj_id, "项目名": xm_name}
    context['ID'] = ID
    return render(request, '10-项目页面/11-中止项目确认页面/cease_project_cause.html', context=context)


#中止成功页面
def stop_item_successful_page(request):
    context = dict()
    xm_id = request.POST.get("xm_id")
    zzyy = request.POST.get("zzyy")
    status, xm_list, reason = api.project_get(xm_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        xm_name = xm_list.name
    #中止：先暂停，后中止
    status1, project_list, reason1 = api.project_services_start()  # 暂停项目
    #status1 = "簇ok"
    if status1 != api.OK:
        ID = {"项目名": xm_name, "错误原因": reason1}
        context['ID'] = ID
        return render(request, '10-项目页面/25-中止项目失败页面/stop_project_failed.html', context=context)
    else:
        #中止项目
        status2, project_list, reason2 = api.project_services_start()  # 暂停项目
        #status2 = "传ok"
        if status2 != api.OK:
            ID = {"项目名": xm_name, "错误原因": reason2}
            context['ID'] = ID
            return render(request, '10-项目页面/25-中止项目失败页面/stop_project_failed.html', context=context)
        else:
            ID = { "项目名": xm_name }
            context['ID'] = ID
            return render(request, '10-项目页面/24-中止项目成功页面/stop_item_successful.html', context=context)


def stop_project_failed_page(request):
    context = dict()
    return render(request, '10-项目页面/25-中止项目失败页面/stop_project_failed.html', context=context)


#执行原因输入页面
def execute_project_cause_page(request, prj_id):
    context = dict()
    status, xm_list, reason = api.project_get(prj_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        # 拿到绑定的充放电机设备ID信息
        xm_name = xm_list.name

    ID = {"项目ID": prj_id, "项目名": xm_name}
    context['ID'] = ID
    return render(request, '10-项目页面/12-执行项目确认页面/execute_project_cause.html', context=context)


#执行成功页面
def execute_item_successful_page(request):
    context = dict()
    xm_id = request.POST.get("xm_id")
    status, xm_list, reason = api.project_get(xm_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        xm_name = xm_list.name
    #执行项目
    status1, project_list, reason1 = api.project_services_start()  # 暂停项目
    #status1 = "NOok"
    if status1 != api.OK:
        ID = {"项目名": xm_name, "错误原因": reason1}
        context['ID'] = ID
        return render(request, '10-项目页面/27-执行项目失败页面/execute_project_failed.html', context=context)
    else:
        ID = {"项目名": xm_name}
        context['ID'] = ID
        return render(request, '10-项目页面/26-执行项目成功页面/execute_item_successful.html', context=context)


def execute_project_failed_page(request):
    context = dict()
    return render(request, '10-项目页面/27-执行项目失败页面/execute_project_failed.html', context=context)


def project_operation_page(request):
    context = dict()
    return render(request, '10-项目页面/13-高级操作页面/project_operation.html', context=context)


def delete_project_page(request):
    status, project_list, reason = api.project_list() # 返回所有状态数据
    context = dict()
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "未通讯/或sid错误")

    context['project_list'] = project_list
    return render(request, '10-项目页面/15-删除所有项目页面/delete_project.html', context=context)


def delete_project_affirm_page(request):
    context = dict()
    return render(request, '10-项目页面/16-删除项目确认页面/delete_project_affirm.html', context=context)


def deleted_item_successful_page(request):
    id = request.POST.get("id")
    ztyy = request.POST.get("scyy")
    status, project_list, reason = api.project_service_stop(id)  # 暂停项目
    #status = "ok"
    if status != api.OK:
        return render(request, '10-项目页面/23-删除项目失败页面/deletion_project_failed.html')
    else:
        return render(request, '10-项目页面/22-删除项目成功页面/deleted_item_successful.html')


def deletion_project_failed_page(request):
    context = dict()
    return render(request, '10-项目页面/23-删除项目失败页面/deletion_project_failed.html', context=context)


def amend_project_affirm_page(request):
    context = dict()
    return render(request, '10-项目页面/18-项目修改确认页面/amend_project_affirm.html', context=context)


def show_main_index_page(request):
    context = dict()
    return render(request, '05-设备四遥选项页面/siyao.html', context=context)


def show_gj_ts_page(request):
    ner = 0
    time = 5
    while ner < time:
        status, lc, reason = api.flow_get_status_from_cache()
        if status != api.OK:
            ner = ner + 1
        else:
            break

    if ner < time:
        state = {"状态":"已连接"}
    else:
        state = {"状态":"未连接"}

    context = dict()
    context['zt'] = state
    return render(request, '07-告警提示页面/alarm_prompt.html', context=context)


def show_sb_set_page(request):
    context = dict()
    return render(request, '09-流程设置页面/step_set.html', context=context)


#其他设备参数设置页面
def parameter_settings_page(request):
    status, cm_list, reason = api.device_get_list_by_type("cm")  # 获取注册水冷机设备列表
    context = dict()
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        context['cm_list'] = cm_list

    status, ec_list, reason = api.device_get_list_by_type("ec")  # 获取注册环境箱设备列表
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        context['ec_list'] = ec_list

    status, cd_list, reason = api.device_get_list_by_type("cd")  # 获取注册充放电机设备列表
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        context['cd_list'] = cd_list

    return render(request, '11-其他设备参数设置页面/parameter_settings.html', context=context)


def parameter_distribution_failure_page(request):
    bz_name = request.POST.get("bz_name")

    status, project_list, reason = api.project_list_configure()  # 下发其他设备参数
    status = "ok"
    context = dict()
    if status != api.OK:
        if bz_name == "zsgc":
            skip = {"设置页面": "zsgc"}
        elif bz_name == "xjxm":
            skip = {"设置页面": "xjxm"}
        context['skip'] = skip
        return render(request, '10-项目页面/31-其他设备参数下发失败页面/parameter_distribution_failure.html', context=context)
    else:
        if bz_name != "xjxm":
            return render(request, '10-项目页面/32-其他设备参数下发成功页面/parameter_distribution_win.html', context=context)
        else:
            return render(request, '06-BMS参数设置页面/aisle_choose.html', context=context)


def parameter_distribution_win_page(request):
    context = dict()
    return render(request, '10-项目页面/32-其他设备参数下发成功页面/parameter_distribution_win.html', context=context)


#完成配置成功页面
def finish_deploy_win_page(request):
    context = dict()
    xm_id = request.POST.get("xm_id")
    status, project_list, reason = api.project_switch_to_ready_status(xm_id)  # 更改项目状态-就绪状态
    #status, project_list, reason = api.project_list()  # 下发BMS参数
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        ID = {"项目ID": xm_id,"项目名":project_list.name}
        context['ID'] = ID
        return render(request, '10-项目页面/35-完成配置成功页面/finish_deploy_win.html', context=context)


#新建项目项目名输入页面
def new_project_name_cause_page(request):
    context = dict()
    #xm_id = request.POST.get("xm_id")
    #if xm_id != None:
    #    status, xm_list, reason = api.project_get(xm_id)  # 获取对应项目ID信息
    #    if status != api.OK:
    #        context['reason'] = reason
    #        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    #    else:
            # 把项目的上传文件信息带下去
    #        project_list = [{"项目流程文件ID": "123", "项目流程文件名": "充电流程"}, {"项目流程文件ID": "153", "项目流程文件名": "放电流程"}]
    #        context['project_list'] = project_list
    #        ID = {"项目ID": xm_id, "进入状态": "完成项目"}
    #        context['ID'] = ID
    #        return render(request, '10-项目页面/34-新建执行项目确认页面/execute_confirmation_page.html', context=context)
    #else:
    #ID = {"进入状态": "新建项目"}
    #context['ID'] = ID
    return render(request, '10-项目页面/14-新建项目项目名输入页面/new_project_name_cause.html', context=context)


# 新建项目名下发失败页面
def failed_issue_project_name_page(request):           #从项目页面进入，把项目名下发，成功进入BMS参数设置，失败报错
    prj_name = request.POST.get("prj_name")
    sn = request.POST.get("sn")
    subscript = request.POST.get("subscript")
    description = request.POST.get("description")
    comment = request.POST.get("comment")
    status, project_list, reason = api.project_create(prj_name,sn,subscript,description,comment)  # 下发新建项目信息
    xm_id = project_list.id
    xm_name = project_list.name
    ID = {"项目ID": xm_id, "项目名": xm_name, "进入状态": "新建项目"}
   #status = "ok"
    context = dict()
    if status != api.OK:
        context['reason'] = reason
        return render(request, '10-项目页面/28-新建项目名下发失败页面/failed_issue_project_name.html', context=context)
    else:
        #status, cm_id, reason = api.device_get_default("cm")  # 获取水冷机设备默认的设备对象
        #if status != api.OK:
            #context['reason'] = reason
            #return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        #else:
            #context['cm_id'] = cm_id

        #status, ec_id, reason = api.device_get_default("ec")  # 获取环境箱设备默认的设备对象
        #if status != api.OK:
            #context['reason'] = reason
            #return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        #else:
            #context['ec_id'] = ec_id

        #status, cd_id, reason = api.device_get_default("cd")  # 获取充放电机设备默认的设备对象
        #if status != api.OK:
            #context['reason'] = reason
            #return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        #else:
            #context['cd_id'] = cd_id

        status, cm_list, reason = api.device_get_list_by_type("cm")  # 获取注册水冷机设备列表
        if status != api.OK:
            context['reason'] = reason
            return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        else:
            context['cm_list'] = cm_list

        status, ec_list, reason = api.device_get_list_by_type("ec")  # 获取注册环境箱设备列表
        if status != api.OK:
            context['reason'] = reason
            return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        else:
            context['ec_list'] = ec_list

        status, cd_list, reason = api.device_get_list_by_type("cd")  # 获取注册充放电机设备列表
        if status != api.OK:
            context['reason'] = reason
            return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        else:
            context['cd_list'] = cd_list

        status, bms_list, reason = api.device_get_list_by_type("bms")  # 获取注册BMS设备列表
        if status != api.OK:
            return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
        else:      #拿数据例子：id = bms_list[0].id   #vendor = bms_list[1].vendor
            context['bms_list'] = bms_list

        context['ID'] = ID
        return render(request, '06-BMS参数设置页面/aisle_choose.html', context=context)


#BMS参数设置页面
def show_begin_index_page(request):     #从项目页面进入，把项目名下发，成功进入BMS参数设置，失败报错
    context = dict()
    xm_id = request.POST.get("xm_id")
    status, bms_list, reason = api.device_get_list_by_type("bms")  # 获取注册BMS设备列表
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        context['bms_list'] = bms_list

    status, cm_list, reason = api.device_get_list_by_type("cm")  # 获取注册水冷机设备列表
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        context['cm_list'] = cm_list

    status, ec_list, reason = api.device_get_list_by_type("ec")  # 获取注册环境箱设备列表
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        context['ec_list'] = ec_list

    status, cd_list, reason = api.device_get_list_by_type("cd")  # 获取注册充放电机设备列表
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        context['cd_list'] = cd_list

    status, bd_bms_list, reason = api.project_get_device_by_type(xm_id,"bms")  # 获取项目绑定BMS设备信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        #拿到绑定的BMS设备ID信息
        bd_bms_id = bd_bms_list.id

    status, bd_cm_list, reason = api.project_get_device_by_type(xm_id, "cm")  # 获取项目绑定水冷机设备信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        # 拿到绑定的水冷机设备ID信息
        bd_cm_id = bd_cm_list.id

    status, bd_ec_list, reason = api.project_get_device_by_type(xm_id, "ec")  # 获取项目绑定环境箱设备信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        # 拿到绑定的环境箱设备ID信息
        bd_ec_id = bd_ec_list.id

    status, bd_cd_list, reason = api.project_get_device_by_type(xm_id, "cd")  # 获取项目绑定充放电机设备信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        # 拿到绑定的充放电机设备ID信息
        bd_cd_id = bd_cd_list.id

    status, xm_list, reason = api.project_get(xm_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        # 拿到绑定的充放电机设备ID信息
        xm_name = xm_list.name

    ID = {"BMS_id":bd_bms_id,"cm_id":bd_cm_id,"ec_id":bd_ec_id,"cd_id":bd_cd_id,"zt":"xg","项目ID": xm_id,"项目名":xm_name}
    context['ID'] = ID
    return render(request, '06-BMS参数设置页面/aisle_choose.html', context=context)


#BMS参数下发失败页面
def bms_parameter_issue_failure_page(request):
    xm_id = request.POST.get("xm_id")
    bms_id = request.POST.get("bms_id")
    cm_id = request.POST.get("cm_id")
    ec_id = request.POST.get("ec_id")
    cd_id = request.POST.get("cd_id")
    #bz_name = request.POST.get("bz_name")
    context = dict()
    if len(xm_id) < 7:
        if len(bms_id) < 7 and len(bms_id) > 0:
            status, project_list, reason = api.project_register_device(xm_id, bms_id)  # 下发BMS参数
            #status, project_list, reason = api.project_list()  # 下发BMS参数
            if status != api.OK:
                ID = {"项目ID":xm_id}
                context['ID'] = ID
                reason = {"错误原因": reason.subscript}
                context['reason'] = reason
                return render(request, '10-项目页面/29-BMS参数下发失败页面/bms_parameter_issue_failure.html', context=context)

        if len(cm_id) < 7 and len(cm_id) > 0:
            status, project_list, reason = api.project_register_device(xm_id, cm_id)  # 下发水冷机参数
            #status, project_list, reason = api.project_list()  # 下发BMS参数
            context = dict()
            if status != api.OK:
                ID = {"项目ID": xm_id}
                context['ID'] = ID
                reason = {"错误原因": reason.subscript}
                context['reason'] = reason
                return render(request, '10-项目页面/29-BMS参数下发失败页面/bms_parameter_issue_failure.html', context=context)

        if len(ec_id) < 7 and len(ec_id) > 0:
            status, project_list, reason = api.project_register_device(xm_id, ec_id)  # 下发环境箱参数
            #status, project_list, reason = api.project_list()  # 下发BMS参数
            context = dict()
            if status != api.OK:
                ID = {"项目ID": xm_id}
                context['ID'] = ID
                reason = {"错误原因": reason.subscript}
                context['reason'] = reason
                return render(request, '10-项目页面/29-BMS参数下发失败页面/bms_parameter_issue_failure.html', context=context)

        if len(cd_id) < 7 and len(cd_id) > 0:
            status, project_list, reason = api.project_register_device(xm_id, cd_id)  # 下发充放电机参数
            #status, project_list, reason = api.project_list()  # 下发BMS参数
            context = dict()
            if status != api.OK:
                ID = {"项目ID": xm_id}
                context['ID'] = ID
                reason = {"错误原因": reason.subscript}
                context['reason'] = reason
                return render(request, '10-项目页面/29-BMS参数下发失败页面/bms_parameter_issue_failure.html', context=context)
    else:
        reason = {"错误原因": "项目ID不对"}
        context['reason'] = reason
        return render(request, '10-项目页面/29-BMS参数下发失败页面/bms_parameter_issue_failure.html', context=context)

    status, xm_list, reason = api.project_get(xm_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        xm_name = xm_list.name

    #读取项目流程文件信息
    status, wj_list, reason = api.project_list_flow_file(xm_id)
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        # 拿到绑定的设备ID信息
        context['wj_list'] = wj_list
        ID = {"项目ID": xm_id, "项目名": xm_name, "进入状态": "新建项目"}
        context['ID'] = ID
        return render(request, '10-项目页面/19-项目流程文件上传页面/upload_project_flow.html', context=context)


#项目流程文件上传页面
def upload_project_flow_page(request):
    context = dict()
    xm_id = request.POST.get("xm_id")

    status, xm_list, reason = api.project_get(xm_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        xm_name = xm_list.name

    status, wj_list, reason = api.project_list_flow_file(xm_id)  #读取项目流程文件信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        # 拿到项目中的流程文件信息
        context['wj_list'] = wj_list
        ID = {"项目ID": xm_id, "项目名": xm_name, "进入状态": "修改项目"}
        context['ID'] = ID
        return render(request, '10-项目页面/19-项目流程文件上传页面/upload_project_flow.html', context=context)


#上传文件失败页面
def failed_upload_file_page(request):
    xm_id = request.POST.get("xm_id")
    xm_subscript = request.POST.get("subscript")
    xm_description = request.POST.get("description")

    context = dict()
    if request.method == "POST":  # 请求方法为POST时，进行处理
        myFile = request.FILES.get("myfile", None)  # 获取上传的文件，如果没有文件，则默认为None
        if not myFile:
            #returnHttpResponse("no files for upload!") #没有文件
            reason = { "错误原因": "没有选择文件", "项目ID": xm_id}
            context['reason'] = reason
            return render(request, '10-项目页面/33-上传文件失败页面/failed_upload_file.html', context=context)
        else:
            destination = open(os.path.join("C:\\Users\86182\Desktop\svn\plane-ui\etc", myFile.name), 'wb+')  # 打开特定的文件进行二进制的写操作
            for chunk in myFile.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()

            flow_file_path = myFile.name
            #flow_file_path = ""
            name = xm_subscript
            comment = xm_description
            status, wj_list, reason = api.project_save_flow_file(xm_id, flow_file_path, name, comment)
            if status != api.OK:
                reason = {"错误原因": reason.subscript, "项目ID": xm_id}
                context['reason'] = reason
                return render(request, '10-项目页面/33-上传文件失败页面/failed_upload_file.html', context=context)
            else:
                context['wj_list'] = wj_list
                ID = { "项目ID": xm_id, "进入状态": "新建项目"}
                context['ID'] = ID
                return render(request, '10-项目页面/30-操作选择页面/operation_select.html', context=context)


#操作选择页面，执行还是继续上传
def operation_select_page(request):
    context = dict()
    return render(request, '10-项目页面/30-操作选择页面/operation_select.html', context=context)


#新建执行项目确认页面
def execute_confirmation_page(request):
    context = dict()
    xm_id = request.POST.get("xm_id")

    status, wj_list, reason = api.project_list_flow_file(xm_id)  # 获取对应项目ID信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        #把项目的上传文件信息带下去
        context['wj_list'] = wj_list
    status, xm_list, reason = api.project_get(xm_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        xm_name = xm_list.name

    ID = { "项目ID": xm_id, "项目名": xm_name, "进入状态": "修改项目"}
    context['ID'] = ID
    return render(request, '10-项目页面/34-新建执行项目确认页面/execute_confirmation_page.html', context=context)


#执行失败提示页面
def show_lc_xz_page(request):
    context = dict()
    xm_id = request.POST.get("xm_id")
    wj_id = request.POST.get("wj_id")

    status, xm_list, reason = api.project_get(xm_id)  # 获取项目信息
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)
    else:
        xm_name = xm_list.name

    status, project_list, reason = api.project_switch_to_ready_status(xm_id)  # 更改项目状态-就绪状态
    if status != api.OK:
        context['reason'] = reason
        return render(request, "07-告警提示页面/alarm_prompt.html", context=context)

    status, project_list, reason = api.flow_run(xm_id, wj_id)  # 执行项目
    if status != api.OK:
        reason = {"错误原因": reason, "项目名":xm_name}
        context['reason'] = reason
        return render(request, '12-执行失败提示页面/execution_failure.html', context=context)
    else:
        return render(request, '08-流程显示页面/article_show.html', context=context)


#流程显示页面
def show_lc_set_page(request):
    context = dict()
    status, lc, reason = api.flow_get_status_from_cache()
    if status != api.OK:
        return render(request, "07-告警提示页面/alarm_prompt.html")
        # return render(request, "未通讯/或sid错误")

    # TODO：这里先判断流程运行状态，提前做显示分支处理
    if lc['流程运行状态'] == '运行中':
        context['lc'] = lc
        return render(request, '08-流程显示页面/article_show.html', context=context)
    else:
        # TODO：这里渲染没有运行流程时候的页面，这个模板文件也改改
        return render(request, '12-执行失败提示页面/execution_failure.html', context=context)


def test_page(request):
    return render(request, "00-base/test.html")


urlpatterns = [
    path('', home_page_page, name="系统首页"),
    path('<int:prj_id>/pause/', suspend_project_cause_page, name="暂停项目原因输入页面"),
    path('ztxmcgsr/', successful_suspension_project_page, name="暂停项目成功页面"),
    path('ztxmsbsr/', project_suspension_failed_page, name="暂停项目失败页面"),
    path('<int:prj_id>/discontinue/', cease_project_cause_page, name="中止项目确认页面"),
    path('zzxmcg/', stop_item_successful_page, name="中止项目成功页面"),
    path('zzxmsb/', stop_project_failed_page, name="中止项目失败页面"),
    path('<int:prj_id>/execute/', execute_project_cause_page, name="执行项目确认页面"),
    path('zxxmcg/', execute_item_successful_page, name="执行项目成功页面"),
    path('zxxmsb/', execute_project_failed_page, name="执行项目失败页面"),
    path('zsgc/', project_operation_page, name="项目高级操作页面"),
    path('xmmsr/', new_project_name_cause_page, name="新建项目项目名输入页面"),
    path('xmmxf/', failed_issue_project_name_page, name="新建项目名下发失败页面"),
    path('scxm/', delete_project_page, name="删除项目页面"),
    path('scxmqr/', delete_project_affirm_page, name="删除项目确认页面"),
    path('scxmcg/', deleted_item_successful_page, name="删除项目成功页面"),
    path('scxmsb/', deletion_project_failed_page, name="删除项目失败页面"),
    path('xgxmqr/', amend_project_affirm_page, name="修改项目确认页面"),
    path('xmwjsc/', upload_project_flow_page, name="项目流程文件上传页面"),
    path('sy/', show_main_index_page, name="设备四遥页面"),
    path('sz/', show_sb_set_page, name="流程设置页面"),
    path('xs/', show_lc_set_page, name="流程显示页面"),
    path('ts/', show_gj_ts_page, name="告警提示页面"),
    path('zxsbts/', show_lc_xz_page, name="执行失败提示页面"),
    path('bms/', show_begin_index_page, name="bms参数设置页面"),
    path('bmscsxfsb/', bms_parameter_issue_failure_page, name="bms参数下发失败页面"),
    path('scwjsb/', failed_upload_file_page, name="上传文件失败页面"),
    path('xjzxxmqr/', execute_confirmation_page, name="新建执行项目确认页面"),
    path('wcpzcg/', finish_deploy_win_page, name="完成配置成功页面"),
    path('wcpzcg/', operation_select_page, name="操作选择页面"),

    path('sbcssz/', parameter_settings_page, name="其他设备参数设置页面"),
    path('sbcsszsb/', parameter_distribution_failure_page, name="其他设备参数设置失败页面"),
    path('sbcsszcg/', parameter_distribution_win_page, name="其他设备参数设置成功页面"),

    path('project/', include("storage.views_project")),
    path('device/', include("storage.views_device")),
    path('flowfile/', include("storage.views_flowfile")),
    path('pwf/', include("storage.views_pwf")),
    path('flow/', include("storage.views_flow")),
    path('broadcast/', include("storage.views_broadcast")),
]
urls= (urlpatterns, 'plane', 'plane' )


