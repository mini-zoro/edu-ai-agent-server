#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : serializers.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/14 11:55 
@Version : 1.0
"""
from django.db import transaction
from rest_framework import serializers

from AAServer import constants
from apps.code_dict.services import get_code_name_by_type_and_code
from apps.student.models import Student
from apps.user.serializers import UserInlineSerializer
from apps.user.services import update_user_by_validated_data, create_user_by_validated_data


class StudentSerializer(serializers.ModelSerializer):
    user = UserInlineSerializer(read_only=True)
    identity_name = serializers.SerializerMethodField(read_only=True)
    status_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        exclude = ('create_user', 'update_user', 'is_del')

    def get_identity_name(self, obj):
        return get_code_name_by_type_and_code(obj.identity, constants.CodeDict.CODE_STUDENT_IDENTITY)

    def get_status_name(self, obj):
        return get_code_name_by_type_and_code(obj.status, constants.CodeDict.CODE_STUDENT_STATUS)


class StudentCreateSerializer(serializers.Serializer):
    # 用户字段
    account = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    name = serializers.CharField(max_length=255, allow_blank=True)
    nickname = serializers.CharField(max_length=255, allow_blank=True)
    phone = serializers.CharField(max_length=255, required=False, allow_blank=True)
    email = serializers.CharField(max_length=255, required=False, allow_blank=True)

    # 学生字段
    identity = serializers.IntegerField()
    student_no = serializers.CharField(max_length=32, required=False, allow_blank=True)
    school_no = serializers.CharField(max_length=32, required=False, allow_blank=True)
    enrollment = serializers.DateField(required=False)
    birth_date = serializers.DateField(required=False)
    gender = serializers.IntegerField(required=False)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    status = serializers.IntegerField(required=False, default=0)
    remark = serializers.CharField(required=False, allow_blank=True)

    @transaction.atomic
    def create(self, validated_data):
        # 1. 先创建用户
        _user, _data = create_user_by_validated_data(validated_data, user_type=constants.UserDict.USER_TYPE_STUDENT)  # 固定学生角色

        # 2. 再创建学生
        student = Student.objects.create(
            user=_user,
            **_data,
        )
        return student

class StudentFlatUpdateSerializer(serializers.ModelSerializer):
    # 把 user 表字段“平铺”到顶层
    nickname = serializers.CharField(required=False, allow_blank=False, allow_null=True)
    name = serializers.CharField(required=False, allow_blank=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=False, allow_null=True)
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Student
        fields = ('nickname', 'name', 'phone', 'email',
                  'identity', 'student_no', 'school_no', 'enrollment',
                  'birth_date', 'gender', 'address', 'status', 'remark')

    @transaction.atomic
    def update(self, instance, validated_data):
        # 1. 更新用户信息
        _user, _data = update_user_by_validated_data(instance.user, validated_data)

        # 2. 更新学生信息
        for attr, value in _data.items():
            if attr == 'user':
                setattr(instance, attr, _user)
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance