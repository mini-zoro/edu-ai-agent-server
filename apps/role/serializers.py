#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : serializers.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/25 16:02 
@Version : 1.0
"""

from rest_framework import serializers

from AAServer.common.exceptions import CustomException
from apps.role.models import Role

class RoleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    role_key = serializers.CharField(required=True)
    role_name = serializers.CharField(required=True)
    type = serializers.IntegerField(read_only=True)
    typeName = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Role
        exclude = ('is_del', 'create_user', 'update_user', 'create_time', 'update_time')

    def get_typeName(self, obj):
        type_dict = {
            0: "可选角色",
            1: "系统角色",
            2: "用户自定义角色"
        }
        return type_dict.get(obj.type, "未知")

    def validate_role_key(self, value):
        if Role.objects.filter(role_key=value).exists():
            raise CustomException(detail="角色码已存在")
        return value

