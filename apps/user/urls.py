#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : urls.py.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/11 17:17 
@Version : 1.0
"""
from django.urls import path, include

import apps.user.views

urlpatterns = [
    path('', apps.user.views.get_user_info),
    path('/type', apps.user.views.get_user_by_type),
]