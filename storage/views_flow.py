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


def show_project_flow_summary(request, prj_id):
    """显示项目流程运行信息"""
    context = dict()

    status, active_prj, reason = api.project_get_current()
    if status != api.OK:
        context['reason'] = reason
        return render(request, '14-流程状态/99-流程信息错误.html', context=context)

    if active_prj.id != prj_id:
        context['reason'] = reason
        return render(request, '14-流程状态/99-流程信息错误.html', context=context)

    status, flow_status, reason = api.flow_get_status_from_cache()
    if status != api.OK:
        context['reason'] = reason
        return render(request, '14-流程状态/99-流程信息错误.html', context=context)

    project = Project.objects.get(id=prj_id)

    context['flow_status'] = flow_status
    context['project'] = project
    return render(request, '14-流程状态/03-流程执行概况.html', context=context)


urlpatterns = [
    path('summary/<int:prj_id>/', show_project_flow_summary, name='显示项目流程执行状态')
]
urls = (urlpatterns, 'plane', 'plane')


