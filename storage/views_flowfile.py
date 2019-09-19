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
from storage.views_plane import *


def flow_file_list(request):
    """流程文件列表"""
    context = dict()
    context['flows_file_list'] = FlowFile.objects.all()
    return render(request, '13-流程文件/01-显示所有流程文件.html', context=context)


def show_flow_file_panel(request, fid):
    """显示流程文件操作面板，更新，删除，下载，查看链接"""
    context = dict()

    flow = FlowFile.objects.get(id=fid)
    context['flow'] = flow
    context['version_list'] = FlowFileHistory.objects.filter(flow=flow)
    return render(request, '13-流程文件/03-流程文件内容显示.html', context=context)


def save_upload_file_to_template(request):
    """
    将上传的文件保存到
    :param request:
    :return:
    """


class UploadFlowFile(ViewWrapperBasic):
    def on_get(self, ctx, request):
        ctx['flow'] = FlowFile()
        return render(request, '13-流程文件/02-流程文件上传表单.html', context=ctx)

    def on_post(self, ctx, request):
        upload = request.FILES.get("file", None)  # 获取上传的文件，如果没有文件，则默认为None

        with tempfile.NamedTemporaryFile() as file:
            for chunk in upload.chunks():  # 分块写入文件
                file.write(chunk)

            success, flow, reason = api.flow_save(file.name, request.POST['name'])
            if success != api.OK:
                self.broadcast_error('拒绝接收', reason)
            else:
                try:
                    next_url = '?next={}'.format(request.GET['next'])
                except KeyError:
                    next_url = ''

                txt = '流程文件上传成功<a href="{}{}">查看</a>'.format(reverse('查看流程文件', args=(flow.id,)), next_url)
                self.broadcast_info('上传成功', txt)

        try:
            next_url = request.GET['next']
        except KeyError:
            next_url = request.path

        return HttpResponseRedirect(next_url)


class UpdateFlowFile(ViewWrapperBasic):
    def on_get(self, ctx, request, fid):
        """更新流程文件"""
        try:
            ctx['flow'] = FlowFile.objects.get(id=fid)
        except FlowFile.DoesNotExist:
            ctx['flow'] = FlowFile()
            self.broadcast_error('错误', '流程对象不存在')

        return render(request, '13-流程文件/02-流程文件上传表单.html', context=ctx)

    def on_post(self, ctx, request, fid):
        flow = ctx['flow'] = FlowFile.objects.get(id=fid)
        flow.name = request.POST['name']
        flow.save()
        upload = request.FILES.get("file", None)  # 获取上传的文件，如果没有文件，则默认为None
        if upload:
            with tempfile.NamedTemporaryFile() as file:
                for chunk in upload.chunks():  # 分块写入文件
                    file.write(chunk)

                success, flow, reason = api.flow_update(fid, file.name)
                if success != api.OK:
                    self.broadcast_warn('修改不完全成功', '上传的文件未被接收！')

        try:
            next_url = request.GET['next']
        except KeyError:
            next_url = reverse('查看流程文件', args=(fid,))

        return HttpResponseRedirect(next_url)


def delete_flow_file(request, fid):
    """删除流程文件"""
    try:
        flow = FlowFile.objects.get(id=fid)
        flow.delete()
    except FlowFileHistory.DoesNotExist:
        pass

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = reverse('流程文件列表')

    return HttpResponseRedirect(next_url)


def download_latest_flow_file(request, fid):
    """下载最新的流程文件"""
    try:
        latest_version = FlowFileHistory.objects.filter(flow_id=fid).order_by('id').last()
    except FlowFileHistory.DoesNotExist:
        pass

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = reverse('查看流程文件', args=(fid,))

    return HttpResponseRedirect(next_url)


def delete_flow_file_by_version(request, fid, version):
    """以版本号删除流程文件"""
    try:
        this_version = FlowFileHistory.objects.get(id=version, flow_id=fid)
        this_version.delete()
    except FlowFileHistory.DoesNotExist:
        pass

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = reverse('查看流程文件', args=(fid,))

    return HttpResponseRedirect(next_url)


def download_flow_file_by_version(request, fid, version):
    """以版本号下载流程文件"""
    try:
        this_version = FlowFileHistory.objects.get(id=version, flow_id=fid)
    except FlowFileHistory.DoesNotExist:
        pass

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = reverse('查看流程文件', args=(fid,))

    return HttpResponseRedirect(next_url)


urlpatterns = [
    path('', flow_file_list, name="流程文件列表"),
    path('<int:fid>/', show_flow_file_panel, name="查看流程文件"),
    path('<int:fid>/download/', download_latest_flow_file, name="下载最新的流程文件"),
    path('<int:fid>/delete/', delete_flow_file, name="删除的流程文件"),
    path('<int:fid>/version/<int:version>/delete/', delete_flow_file_by_version, name="按照版本删除流程文件"),
    path('<int:fid>/version/<int:version>/download/', download_flow_file_by_version, name="按照版本下载流程文件"),
    UploadFlowFile('upload/', name="上传流程文件").route(),
    UpdateFlowFile('update/<int:fid>/', name="更新流程文件").route(),
]
urls = (urlpatterns, 'plane', 'plane')


