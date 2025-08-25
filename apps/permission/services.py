#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : services.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/25 15:36 
@Version : 1.0
"""
from apps.permission.models import Permission


def add_permission(parent_id, key, _type, name, grade, des):
    permission = Permission()
    permission.parent_id = parent_id
    permission.key = key
    permission.type = _type
    permission.name = name
    permission.grade = grade
    permission.des = des
    permission.save()
    return permission