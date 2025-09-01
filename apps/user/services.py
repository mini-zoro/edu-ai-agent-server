#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : services.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/14 12:18 
@Version : 1.0
"""

from django.contrib.auth.hashers import make_password
from apps.rbac.utils import bind_role_to_user_by_type
from apps.user.serializers import UserSerializer


def create_user_by_validated_data(validated_data, user_type):
    """
    根据传入的 validated_data 创建用户
    :param validated_data: 序列化器验证后的数据
    :param user_type: 用户类型（1-教师，2-学生）
    :return: 创建的用户对象和剩余的 validated_data
    """
    password = validated_data['password']
    user_fields = {k: validated_data.pop(k) for k in list(validated_data) if k in ['account', 'password', 'name', 'nickname', 'phone', 'email']}

    # user = User.objects.create(
    #     type=user_type,
    #     password=make_password(password),
    #     **user_fields,
    # )

    serializer = UserSerializer(data=user_fields)
    serializer.is_valid(raise_exception=True)
    user = serializer.save(type=user_type, password=make_password(password))

    # 绑定默认角色
    bind_role_to_user_by_type(user, user_type)
    return user, validated_data

def update_user_by_validated_data(user, validated_data):
    """
    根据传入的 validated_data 更新用户信息
    :param user: 要更新的用户对象
    :param validated_data: 序列化器验证后的数据
    :return: 更新后的用户对象和剩余的 validated_data
    """
    user_fields = {k: validated_data.pop(k) for k in list(validated_data) if k in ['name', 'nickname', 'phone', 'email']}

    for attr, value in user_fields.items():
        setattr(user, attr, value)

    user = user.save()
    # serializer = UserSerializer(instance=user, data=user_fields)
    # serializer.is_valid(raise_exception=True)
    # user = serializer.save()

    return user, validated_data