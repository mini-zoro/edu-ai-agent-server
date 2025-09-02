#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : urls.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/9/2 23:42 
@Version : 1.0
"""
from django.urls import path

import apps.university.views

urlpatterns = [
    path('/search', apps.university.views.get_filtered_university_list),
]
