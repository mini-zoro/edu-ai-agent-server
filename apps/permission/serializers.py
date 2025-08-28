#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : serializers.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/17 22:01 
@Version : 1.0
"""
from rest_framework import serializers

from apps.permission.models import Permission, PermissionRole


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'parent', 'key', 'type', 'name', 'grade', 'des']

class PermissionRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionRole
        fields = ('permission', 'role')


class PermissionTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'parent', 'key', 'type', 'name', 'grade', 'des', 'children']

    def get_children(self, obj):
        children = Permission.objects.filter(parent=obj)
        return PermissionTreeSerializer(children, many=True).data