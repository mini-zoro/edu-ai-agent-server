#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : urls.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/25 16:02 
@Version : 1.0
"""
from django.urls import path

import apps.role.views

urlpatterns = [
    path('', apps.role.views.RoleMngView.as_view()),
    path('/all', apps.role.views.get_all_roles),
    path('/user', apps.role.views.UserRoleMngView.as_view()),

]