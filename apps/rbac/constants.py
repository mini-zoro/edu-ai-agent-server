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
from apps.role.models import Role

PERMISSION_KEY = "perm_key"

ROLE_ADMIN = 'sys_admin'
ROLE_TEACHER = 'sys_teacher'
ROLE_STUDENT = 'sys_student'

USER_TYPE_DEFAULT_ROLE = {0: ROLE_ADMIN, 1: ROLE_TEACHER, 2: ROLE_STUDENT}

# 每个角色默认权限码
DEFAULT_PERMS = {
    ROLE_ADMIN: ['page:*', 'api:*', '!api:student:*', '!page:student:*'],  # 除了学生接口
    ROLE_TEACHER: ['page:teacher:*', 'api:teacher:*'],
    ROLE_STUDENT: ['page:student:*', 'api:student:*'],
}

ROLE_OBJ = {
    ROLE_ADMIN: Role(role_key=ROLE_ADMIN, role_name="管理员", des="系统预设角色：管理员", type=1),
    ROLE_TEACHER: Role(role_key=ROLE_TEACHER, role_name="教师", des="系统预设角色：教师", type=1),
    ROLE_STUDENT: Role(role_key=ROLE_STUDENT, role_name="学生", des="系统预设角色：学生", type=1),
}

PERMISSION_OBJ = {

}
