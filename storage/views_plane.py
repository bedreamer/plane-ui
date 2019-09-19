# -*- coding: utf-8 -*-
# author: lijie
from django.urls import path, include, reverse
from django.shortcuts import render
from django.http import *
from storage.models import *
import api as api
import os
import django.utils.timezone as timezone


class ViewWrapperBasic(object):
    """视图处理Wrapper基础类"""
    def __init__(self, path, name=None, methods=None, **kwargs):
        self.path = path
        self.name = name
        self.ctx = dict()

        if methods is None:
            self.allow_method = list()
            for attr in dir(self):
                if attr.find('on_') != 0:
                    continue
                self.allow_method.append(attr[3:].upper())
        else:
            self.allow_method = [m.upper() for m in methods]

        self.kwargs = kwargs

        for method in self.allow_method:
            method_name = ''.join(['on_', method.lower()])
            if not getattr(self, method_name, None):
                raise NotImplementedError('没有实现 {}'.format(method_name))

        if len(self.allow_method) == 0:
            print("** Warning: 没有为path={}, name={}的路由添加任何http请求处理方法!".format(self.path, self.name))

    def route(self):
        """返回路径映射"""
        if self.name:
            return path(self.path, self, name=self.name)
        else:
            return path(self.path, self)

    def _not_supported_method(self):
        """处理不支持的请求方法"""
        return HttpResponseNotAllowed(self.allow_method)

    def _on_no_view(self, ctx, request, **kwargs):
        """没有绑定视图的处理函数"""
        return HttpResponseForbidden()

    def _on_view_error(self, ctx, request, **kwargs):
        """视图出错处理函数"""
        return HttpResponseForbidden()

    def pre_process_request(self, request, **kwargs):
        """处理请求的预处理"""
        now = timezone.now()
        ctx = {
            'info_message_list': Message.objects.filter(type='info', show_count__gt=0, expire_datetime__gte=now),
            'warn_message_list': Message.objects.filter(type='warn', show_count__gt=0, expire_datetime__gte=now),
            'error_message_list': Message.objects.filter(type='error', show_count__gt=0, expire_datetime__gte=now),
        }
        return ctx
    #
    # @staticmethod
    # def info_filter_iterator(type, show_count_gt, expire_gte):
    #     for msg in Message.objects.filter(type=type, show_count__gt=show_count_gt, expire_datetime__gte=expire_gte):
    #         yield msg
    #     raise StopIteration

    @staticmethod
    def broadcast_info(title, txt):
        msg = Message(type='info', title=title, show_count=1, txt=txt)
        msg.save()

    @staticmethod
    def broadcast_warn(title, txt):
        msg = Message(type='warn', title=title, show_count=1, txt=txt)
        msg.save()

    @staticmethod
    def broadcast_error(title, txt):
        msg = Message(type='error', title=title, show_count=1, txt=txt)
        msg.save()

    def raise_info(self, title, txt):
        """即时消息"""
        msg = Message(type='info', title=title, show_count=0, txt=txt)
        try:
            self.ctx['im_info_message_list'].append(msg)
        except KeyError:
            self.ctx['im_info_message_list'] = [msg]

    def raise_warn(self, title, txt):
        msg = Message(type='warn', title=title, show_count=0, txt=txt)
        try:
            self.ctx['im_warn_message_list'].append(msg)
        except KeyError:
            self.ctx['im_warn_message_list'] = [msg]

    def raise_error(self, title, txt):
        msg = Message(type='error', title=title, show_count=0, txt=txt)
        try:
            self.ctx['im_error_message_list'].append(msg)
        except KeyError:
            self.ctx['im_error_message_list'] = [msg]

    def __call__(self, request, **kwargs):
        """处理django的request请求"""
        self.ctx = self.pre_process_request(request, **kwargs)
        try:
            method_cb = getattr(self, ''.join(['on_', request.method.lower()]), self._not_supported_method)
            response = method_cb(self.ctx, request, **kwargs)
        except NotImplementedError:
            response = HttpResponseBadRequest()
        except (ValueError, Exception) as e:
            self.broadcast_error('内部请求错误!', str(e))
            response = self._on_view_error(self.ctx, request, **kwargs)

        return response

