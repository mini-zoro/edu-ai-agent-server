#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : urls.py.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/11 15:23 
@Version : 1.0
"""
from django.urls import path, include

urlpatterns = [
    path('/auth', include('apps.auth.urls')),
    path('/user', include('apps.user.urls')),
    path('/resource', include('apps.resource.urls')),
    path('/code', include('apps.code_dict.urls')),
    path('/teacher', include('apps.teacher.urls')),
    path('/student', include('apps.student.urls')),
    path('/permission', include('apps.permission.urls')),
    path('/role', include('apps.role.urls')),
    path('/university', include('apps.university.urls')),
    path('/agent', include('apps.agent.urls')),
]
