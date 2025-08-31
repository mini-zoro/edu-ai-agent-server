#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : serializers.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/11 17:19 
@Version : 1.0
"""
from django.core.validators import RegexValidator
from rest_framework import serializers

from AAServer import constants
from apps.auth.models import User
from apps.auth.utils import get_user_perms
from apps.resource.models import Resource
from apps.resource.serializers import ResourceSerializer
from apps.role.services import get_roles_by_user_id


class UserBaseSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = '__all__'


    def get_avatar_url(self, obj):
        avatar_id = obj.avatar if isinstance(obj, User) else obj['avatar']
        if avatar_id:
            resource = Resource.objects.get(id=avatar_id)
            url = ResourceSerializer(resource).data['remote_file_url']
            return url
        return None

class UserInlineSerializer(UserBaseSerializer):
    class Meta:
        model = User
        exclude = ('password', 'is_del', 'create_user', 'create_time', 'update_time', 'update_user')   # 不暴露敏感字段

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[
        RegexValidator(
            regex=constants.UserDict.USER_PASSWORD_REGEX,
            message='密码必须 8-20 位，且包含字母、数字'
        )
    ])

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ("id",)


class UserInfoSerializer(UserSerializer):
    """
    用户信息序列化器
    """
    permission_keys = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = User
        exclude = ('is_del', 'create_time', 'update_time', 'create_user', 'update_user')

    def get_permission_keys(self, obj):
        return get_user_perms(obj)

class UserSessionSerializer(serializers.ModelSerializer):
    """
    用户会话信息序列化器
    """
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        exclude = ('password', 'is_del', 'create_time', 'update_time', 'create_user', 'update_user')

    def get_permissions(self, obj):
        return get_user_perms(obj)

class UserWithRolesSerializer(UserInlineSerializer):
    """
    用户角色列表序列化器
    """
    roles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        exclude = ('password', 'is_del', 'create_user', 'create_time', 'update_time', 'update_user')

    def get_roles(self, obj):
        from apps.role.serializers import RoleSerializer
        roles = get_roles_by_user_id(obj.id)
        return RoleSerializer(roles, many=True).data