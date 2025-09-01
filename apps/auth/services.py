#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : services.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/6 17:19 
@Version : 1.0
"""
import uuid
from datetime import timezone

from django.core.cache import cache
from django.forms import model_to_dict

from AAServer import redis_util
from AAServer.common.authentication import generate_token
from AAServer.utils.RedisUtils import CacheKeys
from apps.auth.utils import get_user_perms_from_db
from django.utils import timezone


def do_login(user):
    """
    处理登录
    :param user: 登录用户
    :return: 登录信息
    """
    # 生成AccessToken
    access_token = generate_token()

    # 获取用户权限
    permissions = get_user_perms_from_db(user)

    # 存入缓存
    user_info = model_to_dict(user, exclude=['create_time', 'update_time', 'password', 'create_user', 'update_user', 'is_del', 'expire_time', 'last_login'])
    user_info['permissions'] = permissions

    redis_util.set_object(CacheKeys.TOKEN_USER + str(access_token), user_info, timeout=3600 * 24)  # 有效期为24小时
    # cache.set(CacheKeys.TOKEN_USER + str(access_token), user_info, timeout=3600 * 24)  # 同步到Django缓存

    user.last_login = timezone.now()
    user.save()

    # 响应结果
    return {
        'token': str(access_token),
    }