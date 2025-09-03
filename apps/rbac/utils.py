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
from AAServer import redis_util
from AAServer.utils.RedisUtils import CacheKeys
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

def clear_perms_cache():
    """
    清除权限相关缓存
    """
    keys = redis_util.get_all_keys()
    to_del_keys = [k for k in keys if k.startswith(CacheKeys.USER_PERMISSIONS)]
    for k in to_del_keys:
        redis_util.delete_value(k)
    redis_util.delete_value(CacheKeys.PERMISSION_TREE)