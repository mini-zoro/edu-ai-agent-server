#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : urls.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/17 22:01 
@Version : 1.0
"""
from django.urls import path

import apps.permission.views

urlpatterns = [
    path('', apps.permission.views.PermissionView.as_view()),
    path('/role/<int:role_id>', apps.permission.views.get_permission_by_role),
    path('/tree', apps.permission.views.get_permission_tree)
]
