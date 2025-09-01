#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : utils.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/9/1 15:44 
@Version : 1.0
"""
from apps.rbac.constants import USER_TYPE_DEFAULT_ROLE
from apps.role.models import Role, UserRole


def bind_role_to_user_by_type(user, user_type):
    """
    通过用户类型绑定角色
    :param user: 用户对象
    :param user_type: 用户类型
    """
    role_key = USER_TYPE_DEFAULT_ROLE[user_type]
    role = Role.objects.get(role_key=role_key)
    UserRole.objects.create(user=user, role=role)