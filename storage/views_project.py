# -*- coding: utf-8 -*-
# author: lijie
from django.urls import path, include, reverse
from django.shortcuts import render
from django.http import *
from storage.models import *
import api as api
import os
import storage.views_plane as plane
import flowfile
import tempfile
import codecs


class ProjectViewBasic(plane.ViewWrapperBasic):
    """项目相关的视图基类"""
    def pre_process_request(self, request, **kwargs):
        ctx = super().pre_process_request(request, **kwargs)
        ctx['PRJ_STATUS_INIT'] = profile.PRJ_STATUS_INIT
        ctx['PRJ_STATUS_CONFIGURE'] = profile.PRJ_STATUS_CONFIGURE
        ctx['PRJ_STATUS_READY'] = profile.PRJ_STATUS_READY
        ctx['PRJ_STATUS_RUNNING'] = profile.PRJ_STATUS_RUNNING
        ctx['PRJ_STATUS_PAUSE'] = profile.PRJ_STATUS_PAUSE
        ctx['PRJ_STATUS_DONE'] = profile.PRJ_STATUS_DONE
        ctx['PRJ_STATUS_ABORT'] = profile.PRJ_STATUS_ABORT
        ctx['PRJ_STATUS_END'] = profile.PRJ_STATUS_END
        ctx['running_project_list'] = Project.objects.filter(status=profile.PRJ_STATUS_RUNNING)
        return ctx


class ProjectStatusViewBasic(ProjectViewBasic):
    """项目状态相关内容处理视图"""
    filter_status = ''

    def pre_process_request(self, request, **kwargs):
        ctx = super().pre_process_request(request, **kwargs)
        ctx['view_name'] = self.name

        ctx['project_list'] = Project.objects.filter(status=self.filter_status)
        return ctx


class ProjectSummaryView(ProjectStatusViewBasic):
    """项目概要页面处理视图"""
    def pre_process_request(self, request, **kwargs):
        ctx = super().pre_process_request(request, **kwargs)
        ctx['running_project_list'] = Project.objects.filter(status=profile.PRJ_STATUS_RUNNING)
        ctx['ready_project_list'] = Project.objects.filter(status=profile.PRJ_STATUS_READY)
        ctx['configure_project_list'] = Project.objects.filter(status=profile.PRJ_STATUS_CONFIGURE)
        ctx['pause_project_list'] = Project.objects.filter(status=profile.PRJ_STATUS_PAUSE)
        ctx['done_project_list'] = Project.objects.filter(status=profile.PRJ_STATUS_DONE)
        ctx['aborted_project_list'] = Project.objects.filter(status=profile.PRJ_STATUS_ABORT)
        return ctx

    def on_get(self, ctx, request):
        return render(request, "10-项目页面/99-summary.html", context=ctx)


class ProjectRunningView(ProjectStatusViewBasic):
    """执行项目的页面处理视图"""
    filter_status = profile.PRJ_STATUS_RUNNING

    def on_get(self, ctx, request):
        if len(ctx['project_list']) == 1:
            project = ctx['project_list'].first()
            ctx['project'] = project

            # 和项目关联的设备
            ctx['project_with_device'] = ProjectWithDevice.objects.filter(project=project)
            # 和项目关联的流程文件
            ctx['project_with_flow_files_list'] = ProjectWithFlow.objects.filter(project=project)

            # 流程操作面板
            try:
                ctx['active_pwf'] = active_pwf = ProjectWithFlow.objects.get(project=project, active=True)
            except ProjectWithFlow.DoesNotExist:
                ctx['active_pwf'] = active_pwf = None

            # 项目关联的设备驱动服务状态
            status, srv_status, reason = api.project_service_status(project.id)
            if status != api.OK:
                ctx['device_driver_ready'] = device_driver_ready = False
            else:
                if False in [s['服务中'] for s in srv_status] or len(srv_status) == 0:
                    ctx['device_driver_ready'] = device_driver_ready = False
                else:
                    ctx['device_driver_ready'] = device_driver_ready = True

            if device_driver_ready is False:
                txt = '项目 "{}" 服务未就绪，<a class="text-danger" href="{}?next={}">' \
                      '<span class="glyphicon glyphicon-play-circle"></span>启动</a>'.\
                    format(project.name, reverse('启动项目服务', args=(project.id,)), request.path)
                self.raise_warn('服务未就绪', txt)

            success, flowd, reason = api.flow_get_status_from_root()
            ctx['flowd'] = flowd

        return render(request, '10-项目页面/04-执行项目详情页面/execute_details.html', context=ctx)


class ProjectReadyView(ProjectStatusViewBasic):
    """就绪项目的页面处理视图"""
    filter_status = profile.PRJ_STATUS_READY

    def on_get(self, ctx, request):
        return render(request, '10-项目页面/05-所有就绪项目罗列页面/ready_project.html', context=ctx)


class ProjectPauseView(ProjectStatusViewBasic):
    """暂停项目的页面处理视图"""
    filter_status = profile.PRJ_STATUS_PAUSE

    def on_get(self, ctx, request):
        return render(request, '10-项目页面/06-所有暂停项目罗列页面/suspend_project.html', context=ctx)


class ProjectConfigureView(ProjectStatusViewBasic):
    """配置项目的页面处理视图"""
    filter_status = profile.PRJ_STATUS_CONFIGURE

    def on_get(self, ctx, request):
        return render(request, '10-项目页面/07-所有配置项目罗列页面/configuration_project.html', context=ctx)


class ProjectDoneView(ProjectStatusViewBasic):
    """完成项目的页面处理视图"""
    filter_status = profile.PRJ_STATUS_DONE

    def on_get(self, ctx, request):
        return render(request, '10-项目页面/08-所有完成项目罗列页面/accomplish_project.html', context=ctx)


class ProjectAbortView(ProjectStatusViewBasic):
    """中止项目的页面处理视图"""
    filter_status = profile.PRJ_STATUS_ABORT

    def on_get(self, ctx, request):
        return render(request, '10-项目页面/08-所有中止项目罗列页面/abort_project.html', context=ctx)


def project_create(request):
    context = dict()
    if request.method == 'GET':
        context['project'] = Project()
        return render(request, '10-项目页面/03-项目编辑表单/project-form.html', context=context)
    else:
        status, project, reason = api.project_create(request.POST['name'], request.POST['sn'], request.POST['subscript'], request.POST['description'], request.POST['comment'])

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = reverse('按照设备类型修改页面', args=(project.id, 'bms'))

    return HttpResponseRedirect(next_url)


def project_change_profile(request, prj_id):
    """
    更改项目配置数据
    :param request: http请求
    :param prj_id: 项目ID
    :return:
    """
    context = dict()

    try:
        project = Project.objects.get(id=prj_id)
        context['project'] = project
    except Project.DoesNotExist:
        context['reason'] = '\n'.join(['修改项目参数:', '无法找到id={}的项目记录!'.format(prj_id)])
        context['next'] = reverse('项目概要页面')
        return render(request, "00-base/global-error.html", context)

    if request.method == 'GET':
        return render(request, '10-项目页面/03-项目编辑表单/project-form.html', context=context)

    project.name = request.POST['name']
    project.sn = request.POST['sn']
    project.subscript = request.POST['subscript']
    project.description = request.POST['description']
    project.save()

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = reverse('项目概要页面')

    return HttpResponseRedirect(next_url)


def project_device_summary(request, prj_id):
    context = dict()

    try:
        project = Project.objects.get(id=prj_id)
        context['project'] = project
    except Project.DoesNotExist:
        context['reason'] = '\n'.join(['修改项目参数:', '无法找到id={}的项目记录!'.format(prj_id)])
        context['next'] = reverse('项目概要页面')
        return render(request, "00-base/global-error.html", context)

    context['project_with_device'] = ProjectWithDevice.objects.filter(project=project)
    return render(request, '10-项目页面/03-项目编辑表单/project-with-device-list.html', context=context)


def project_change_device_by_type(request, prj_id, dev_type):
    """按照设备类型修改"""
    context = dict()

    try:
        project = Project.objects.get(id=prj_id)
        context['project'] = project
    except Project.DoesNotExist:
        context['reason'] = '\n'.join(['修改项目参数:', '无法找到id={}的项目记录!'.format(prj_id)])
        context['next'] = reverse('项目概要页面')
        return render(request, "00-base/global-error.html", context)

    if request.method == 'GET':
        try:
            dtype = PlaneDeviceType.objects.get(code=dev_type)
        except PlaneDeviceType.DoesNotExist:
            context['reason'] = '\n'.join(['按照设备类型修改:', '无法为id={}的项目查询到类型为{}的设备类型记录!'.format(prj_id, dev_type)])
            context['next'] = reverse('项目概要页面')
            return render(request, "00-base/global-error.html", context)

        all_device = PlaneDevice.objects.filter(type=dtype)
        selected_devices_list = ProjectWithDevice.objects.filter(project=project, device__type=dtype)

        if len(selected_devices_list):
            prj_select_device = selected_devices_list[0].device
        else:
            prj_select_device = None

        context['project'] = project
        context['dev_type_list'] = PlaneDeviceType.objects.all().order_by('-code')
        context['prj_select_device'] = prj_select_device
        context['all_device'] = all_device
        context['dtype'] = dtype
        context['code'] = dev_type

        try:
            context['prev'] = request.GET['prev']
        except KeyError:
            dev_code_list = [t.code for t in PlaneDeviceType.objects.all().order_by('code')]
            dev_code_list.insert(0, None)
            idx = dev_code_list.index(dev_type)
            next_dev_type = dev_code_list[idx-1]
            if next_dev_type:
                context['prev'] = reverse('按照设备类型修改页面', args=(prj_id, next_dev_type))

        try:
            context['next'] = request.GET['next']
        except KeyError:
            context['next'] = reverse('项目概要页面')

        return render(request, '10-项目页面/03-项目编辑表单/project-with-device-form.html', context=context)

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = request.path

    selected_devices_id = int(request.POST[dev_type])
    if selected_devices_id == -1:
        pwd_list = ProjectWithDevice.objects.filter(project_id=prj_id, device__type__code=dev_type)
        for pwd in pwd_list:
            api.project_unregister_device(prj_id, pwd.device.id)
        return HttpResponseRedirect(next_url)

    status, _, reason = api.project_register_device(prj_id, selected_devices_id)
    return HttpResponseRedirect(next_url)


def project_with_flow_file(request, prj_id):
    """获取当前项目的流程执行状态"""
    status, project, reason = api.project_get_current()
    if status != api.OK:
        return HttpResponseNotFound()

    if prj_id != project.id:
        return HttpResponseNotFound()

    status, flow_status, reason = api.flow_get_status_from_cache()
    if status != api.OK:
        return HttpResponseNotFound()

    context = dict()
    context['project'] = project
    context['flow_status'] = flow_status

    return render(request, "14-流程状态/03-流程执行概况.html", context=context)


class ProjectDetailView(ProjectViewBasic):
    """显示项目的详细信息"""
    def on_get(self, ctx, request, prj_id):
        project = Project.objects.get(id=prj_id)
        ctx['project'] = project
        ctx['project_status_change_history_list'] = ProjectStateLog.objects.filter(project=project).order_by('-change_datetime')

        # 项目关联的设备
        ctx['project_with_device'] = ProjectWithDevice.objects.filter(project=project)
        # 项目关联的流程文件列表
        ctx['project_with_flow_files_list'] = ProjectWithFlow.objects.filter(project=project)

        # 流程运行状态
        status, flow_status, reason = api.flow_get_status_from_cache()
        ctx['flow_status'] = flow_status

        return render(request, '10-项目页面/98-project-detail.html', context=ctx)


class ProjectStatusChangeView(ProjectViewBasic):
    """项目状态转移基类"""
    def process_done(self, request, prj_id, status, project, reason):
        if status != api.OK:
            self.broadcast_error(title=self.name, txt=reason)

        try:
            next_url = request.GET['next']
        except KeyError:
            next_url = reverse(self.name, args=(project.id, ))

        return HttpResponseRedirect(next_url)


class ProjectStatus2ReadyView(ProjectStatusChangeView):
    """项目状态转就绪"""
    def on_get(self, ctx, request, prj_id):
        status, project, reason = api.project_switch_to_ready_status(prj_id)
        return self.process_done(request, prj_id, status, project, reason)


class ProjectStatus2RunningView(ProjectStatusChangeView):
    """项目状态转执行"""
    def on_get(self, ctx, request, prj_id):
        pwd_list = ProjectWithDevice.objects.filter(project_id=prj_id)
        if len(pwd_list) > 0:
            status, project, reason = api.project_switch_to_running_status(prj_id)
        else:
            href = reverse('按照设备类型修改页面', args=(prj_id, 'bms'))
            status, project, reason = api.ERROR, None, '项目需要绑定至少一个设备才能执行！现在就去<a href="{}">关联</a>设备。'.format(href)

        return self.process_done(request, prj_id, status, project, reason)


class ProjectStatus2PauseView(ProjectStatusChangeView):
    """项目状态转暂停"""
    def on_get(self, ctx, request, prj_id):
        status, project, reason = api.project_switch_to_pause_status(prj_id)
        return self.process_done(request, prj_id, status, project, reason)


class ProjectStatus2AbortView(ProjectStatusChangeView):
    """项目状态转中止"""
    def on_get(self, ctx, request, prj_id):
        status, project, reason = api.project_switch_to_abort_status(prj_id)
        return self.process_done(request, prj_id, status, project, reason)


class ProjectStatus2DoneView(ProjectStatusChangeView):
    """项目状态转完成"""
    def on_get(self, ctx, request, prj_id):
        status, project, reason = api.project_switch_to_done_status(prj_id)
        return self.process_done(request, prj_id, status, project, reason)


class ProjectServiceView(ProjectViewBasic):
    """项目服务视图基类"""
    def process_done(self, request, prj_id, status, service_status, reason):
        if status != api.OK:
            self.broadcast_error(title=self.name, txt=reason)

        try:
            next_url = request.GET['next']
        except KeyError:
            self.broadcast_warn(title=self.name, txt="没有执行next，自动转换至项目详情")
            next_url = reverse('项目详细信息展示页面', args=(prj_id, ))

        return HttpResponseRedirect(next_url)


class ProjectServiceStart(ProjectServiceView):
    """启动项目服务"""
    def on_get(self, ctx, request, prj_id):
        status, service_status, reason = api.project_services_start(prj_id)
        for ps in service_status:
            if not ps['服务中']:
                self.broadcast_error(title='无法启动服务', txt='启动设备{}服务失败'.format(ps['dev_name']))
            else:
                self.broadcast_info(title='启动成功', txt='启动设备{}服务成功'.format(ps['dev_name']))

        return self.process_done(request, prj_id, status, service_status, reason)


class ProjectServiceStop(ProjectServiceView):
    """停止项目服务"""
    def on_get(self, ctx, request, prj_id):
        status, service_status, reason = api.project_service_stop(prj_id)
        for ps in service_status:
            if ps['服务中']:
                self.broadcast_error(title='无法关闭服务', txt='关闭设备{}服务失败'.format(ps['dev_name']))
            else:
                self.broadcast_info(title='停止成功', txt='停止设备{}服务成功'.format(ps['dev_name']))

        return self.process_done(request, prj_id, status, service_status, reason)


class ProjectServiceRestart(ProjectServiceView):
    """重启项目服务"""
    def on_get(self, ctx, request, prj_id):
        status, service_status, reason = api.project_service_restart(prj_id)
        return self.process_done(request, prj_id, status, service_status, reason)


class ProjectServiceStatus(ProjectServiceView):
    """项目服务状态"""
    def on_get(self, ctx, request, prj_id):
        status, service_status, reason = api.project_service_status(prj_id)
        return self.process_done(request, prj_id, status, service_status, reason)


def download_template_for_project(request, prj_id):
    project = Project.objects.get(id=prj_id)
    full_tmp_file = tempfile.mktemp()
    flow = flowfile.FlowFileWriter(full_tmp_file)
    devices_list = project.get_depended_device_list()
    flow.create_template_for_device(devices_list)
    flow.save()

    def file_iterator(file_path, chunk_size=1024):
        with codecs.open(file_path, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if chunk:
                    yield chunk
                else:
                    break

    r = StreamingHttpResponse(file_iterator(full_tmp_file))
    r['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    r['Content-Disposition'] = 'attachment;filename="项目{}的流程模板.xlsx"'.format(prj_id)
    return r


class ProjectWithFlowControlView(plane.ViewWrapperBasic):
    """流程控制基类"""
    pass


class PWFControlStart(ProjectWithFlowControlView):
    """控制启动流程"""

    def on_get(self, ctx, request, prj_id, fid):
        try:
            pwf = ProjectWithFlow.objects.get(project_id=prj_id, flow_id=fid)
            success, _, reason = api.flow_run(prj_id, fid)
            if success != api.OK:
                self.broadcast_error('失败', reason)
            else:
                pwf.active = True
                pwf.save()
                self.broadcast_info('成功', '已开始id={}的流程'.format(prj_id, fid))
        except ProjectWithFlow.DoesNotExist:
            self.broadcast_error('对象错误', 'id={}的项目没有绑定过id={}的流程'.format(prj_id, fid))

        try:
            next_url = request.GET['next']
        except KeyError:
            next_url = reverse('执行项目详情页面')

        return HttpResponseRedirect(next_url)


class PWFControlStop(ProjectWithFlowControlView):
    """控制停止流程"""

    def on_get(self, ctx, request, prj_id, fid):
        try:
            pwf = ProjectWithFlow.objects.get(project_id=prj_id, flow_id=fid)
            success, _, reason = api.flow_stop()
            pwf.active = False
            pwf.save()

            self.broadcast_info('成功', '已停止id={}的流程'.format(prj_id, fid))
        except ProjectWithFlow.DoesNotExist:
            self.broadcast_error('对象错误', 'id={}的项目没有绑定过id={}的流程'.format(prj_id, fid))

        try:
            next_url = request.GET['next']
        except KeyError:
            next_url = reverse('执行项目详情页面')

        return HttpResponseRedirect(next_url)


urlpatterns = [
    # 按项目状态分类的列表
    ProjectSummaryView(path='summary/', name="项目概要页面").route(),
    ProjectRunningView(path='running/list/', name="执行项目详情页面").route(),
    ProjectReadyView(path='ready/list/', name="就绪项目罗列页面").route(),
    ProjectPauseView(path='pause/list/', name="暂停项目罗列页面").route(),
    ProjectConfigureView(path='configure/list/', name="配置项目罗列页面").route(),
    ProjectDoneView(path='done/list/', name="完成项目罗列页面").route(),
    ProjectAbortView(path='abort/list/', name="中止项目罗列页面").route(),

    path('create/', project_create, name="新建项目页面"),

    ProjectDetailView(path='<int:prj_id>/', name="项目详细信息展示页面").route(),
    path('<int:prj_id>/change/', project_change_profile, name="修改项目页面"),

    # 项目状态切换
    ProjectStatus2ReadyView(path='<int:prj_id>/status/to/ready/', name="项目转就绪").route(),
    ProjectStatus2RunningView(path='<int:prj_id>/status/to/running/', name="项目转执行").route(),
    ProjectStatus2PauseView(path='<int:prj_id>/status/to/pause/', name="项目转暂停").route(),
    ProjectStatus2AbortView(path='<int:prj_id>/status/to/abort/', name="项目转中止").route(),
    ProjectStatus2DoneView(path='<int:prj_id>/status/to/done/', name="项目转完成").route(),

    # 项目服务管理
    ProjectServiceStart('<int:prj_id>/service/start/', name="启动项目服务").route(),
    ProjectServiceStop('<int:prj_id>/service/stop/', name="停止项目服务").route(),
    ProjectServiceRestart('<int:prj_id>/service/restart/', name="重启项目服务").route(),
    ProjectServiceStatus('<int:prj_id>/service/status/', name="项目服务状态").route(),

    path('<int:prj_id>/device/', project_device_summary, name="项目关联设备信息页面"),
    path('<int:prj_id>/device/<str:dev_type>/', project_change_device_by_type, name="按照设备类型修改页面"),

    path('<int:prj_id>/flow/', project_with_flow_file, name="项目流程信息页面"),
    PWFControlStart('<int:prj_id>/flow/<int:fid>/start/', name="执行流程").route(),
    PWFControlStop('<int:prj_id>/flow/<int:fid>/stop/', name="停止流程").route(),

    path('<int:prj_id>/流程模板.xlsx', download_template_for_project, name="下载项目的流程文件模板"),
]
urls= (urlpatterns, 'plane', 'plane')


