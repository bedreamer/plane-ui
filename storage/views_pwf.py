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


def show_flow_files_linked_to_project(request, prj_id):
    """显示链接到项目的流程文件列表"""
    context = dict()
    pwf = ProjectWithFlow.objects.filter(project_id=prj_id)
    context['pwf'] = pwf

    context['prj_id'] = prj_id
    context['project'] = Project.objects.get(id=prj_id)
    status, context['flows'], reason = api.project_list_flow_file(prj_id)
    context['flow_file_list'] = FlowFile.objects.all()
    return render(request, "13-流程文件/04-项目的关联流程文件列表.html", context=context)


def show_projects_linked_to_flow_file(request, fid):
    """显示链接到流程文件的项目列表"""
    context = dict()
    pwf = ProjectWithFlow.objects.filter(flow_id=fid)
    context['pwf'] = pwf
    return render(request, "13-流程文件/04-流程文件的关联项目列表.html", context=context)


def link_flow_file_to_project(request, fid, prj_id):
    """将流程文件链接至项目"""
    status, _, reason = api.project_bind_flow_file(prj_id, fid)

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = reverse('pwf显示链接到项目的流程文件列表', args=(prj_id,))

    return HttpResponseRedirect(next_url)


def unlink_flow_file_from_project(request, fid, prj_id):
    """解除流程文件至项目的链接"""
    status, _, reason = api.project_unbind_flow_file(prj_id, fid)

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = reverse('pwf显示链接到项目的流程文件列表', args=(prj_id,))

    return HttpResponseRedirect(next_url)


urlpatterns = [
    path('project/<int:prj_id>/', show_flow_files_linked_to_project, name='pwf显示链接到项目的流程文件列表'),
    path('file/<int:fid>/', show_projects_linked_to_flow_file, name='pwf显示链接到流程文件的项目列表'),
    path('link/file/<int:fid>/to/project/<int:prj_id>/', link_flow_file_to_project, name='pwf将流程文件链接至项目'),
    path('unlink/file/<int:fid>/to/project/<int:prj_id>/', unlink_flow_file_from_project, name='pwf解除流程文件至项目的链接'),
]
urls = (urlpatterns, 'plane', 'plane')


