#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : utils.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/7 16:04 
@Version : 1.0
"""
import json

from AAServer import redis_util
from AAServer.utils.RedisUtils import CacheKeys
from apps.auth.models import User

from apps.permission.models import Permission
from apps.permission.serializers import PermissionSerializer


def get_user_perms_from_db(user) -> list:
    """
    从数据库获取用户权限
    :param user: 用户对象
    :return: set: 用户权限集合
    """
    if user.type == 0:  # 管理员
        # 超级管理员拥有所有权限
        qs = Permission.objects.all()
    else:
        qs = Permission.objects.filter(
            permissionrole__role__userrole__user=user,
            permissionrole__role__userrole__user__is_del=0
        ).values_list('name', flat=True).distinct()
    return PermissionSerializer(qs, many=True).data


def get_user_perms(user) -> list:
    """
    获取用户权限，使用缓存优化性能
    :param user: 用户对象
    :return: set: 用户权限集合
    """
    # 兼容 dict / User 实例
    user_id = user['id'] if isinstance(user, dict) else user.id

    permission_list = redis_util.get_object(CacheKeys.USER_PERMISSIONS + str(user_id))
    if permission_list:
        return permission_list
    else:
        perms = get_user_perms_from_db(user if isinstance(user, User) else User.objects.get(id=user_id))
        redis_util.set_object(CacheKeys.USER_PERMISSIONS + str(user_id), perms, timeout=3600 * 24)  # 缓存一天
        return perms

def clear_user_perms_cache(role_id):
    """
    清除拥有某个角色的用户权限缓存
    :param role_id: 角色ID
    :return:
    """
    user_ids = User.objects.filter(userrole__role_id=role_id).values_list('id', flat=True).distinct()
    for user_id in user_ids:
        redis_util.delete(CacheKeys.USER_PERMISSIONS + str(user_id))