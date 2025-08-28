#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : authentication.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/11 14:15 
@Version : 1.0
"""
import json
import uuid

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from AAServer import redis_util
from AAServer.common import exceptions
from AAServer.utils.RedisUtils import CacheKeys
from apps.auth.models import User


class RedisTokenAuthentication(TokenAuthentication):
    keyword = 'Token'
    def authenticate_credentials(self, key):
        user_data = redis_util.get_object(CacheKeys.TOKEN_USER + str(key))
        if user_data:
            user_dict = user_data
            user_obj = User()
            for key_name in user_dict.keys():
                setattr(user_obj, key_name, user_dict[key_name])
            return user_obj, key
        raise AuthenticationFailed

def get_authorization_token(request):
    """
    从请求头中获取Authorization字段的Token
    :param request: 请求对象
    :return: Token字符串或None
    """
    auth = request.headers.get('Authorization')
    if auth and auth.startswith('Token '):
        return auth.split(' ')[1]
    return None

def generate_token():
    """
    生成用户的Token
    :return: Token字符串
    """
    return uuid.uuid4()