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


def broadcast_dismiss(request, mid):
    """清除广播消息"""
    try:
        m = Message.objects.get(id=mid)
        m.show_count -= 1
        m.save()
    except Message.DoesNotExist:
        pass

    return HttpResponse('ok')


urlpatterns = [
    path('<int:mid>/dismiss/', broadcast_dismiss, name="清除消息")
]
urls = (urlpatterns, 'plane', 'plane')
