#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : constants.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/26 23:15 
@Version : 1.0
"""
ROLE_ADMIN   = 'admin'
ROLE_TEACHER = 'teacher'
ROLE_STUDENT = 'student'

# 每个角色默认权限码
DEFAULT_PERMS = {
    ROLE_ADMIN:   ['page:*', 'api:*', '!api:student:*'],   # 除了学生接口
    ROLE_TEACHER: ['page:teacher:*', 'api:teacher:*'],
    ROLE_STUDENT: ['page:student:*', 'api:student:*'],
}