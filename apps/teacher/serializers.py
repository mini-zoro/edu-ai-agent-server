#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : serializers.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/13 15:47 
@Version : 1.0
"""
from django.db import transaction
from rest_framework import serializers

from AAServer import constants
from AAServer.common.exceptions import ValidationException
from apps.code_dict.services import get_code_name_by_type_and_code
from apps.teacher.models import Teacher
from apps.university.models import University
from apps.university.serializers import UniversityInlineSerializer
from apps.user.serializers import UserInlineSerializer
from apps.user.services import create_user_by_validated_data, update_user_by_validated_data


class TeacherSerializer(serializers.ModelSerializer):
    user = UserInlineSerializer(read_only=True)
    university = UniversityInlineSerializer(read_only=True)
    subject_name = serializers.SerializerMethodField(read_only=True)
    professional_title_name = serializers.SerializerMethodField(read_only=True)
    profession_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Teacher
        exclude = ('create_user', 'update_user', 'is_del')

    def get_profession_name(self, obj):
        name = get_code_name_by_type_and_code(code=obj.profession, code_type=constants.CodeDict.CODE_TEACHER_PROFESSION)
        if not name:
            return "暂无"
        return name

    def get_professional_title_name(self, obj):
        name = get_code_name_by_type_and_code(code=obj.profession, code_type=constants.CodeDict.CODE_TEACHER_TITLE)
        if not name:
            return "暂无"
        return name

    def get_subject_name(self, obj):
        name = get_code_name_by_type_and_code(code=obj.subject, code_type=constants.CodeDict.CODE_SUBJECT)
        if not name:
            return "暂无"
        return name


class TeacherCreateSerializer(serializers.Serializer):
    # 用户字段
    account = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    name = serializers.CharField(max_length=255)
    nickname = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255, required=False, allow_blank=True)

    # 教师字段
    birth_date = serializers.DateField()
    gender = serializers.IntegerField()
    university_id = serializers.IntegerField()
    subject = serializers.IntegerField()
    professional_title = serializers.IntegerField()
    profession = serializers.IntegerField()
    department = serializers.CharField(max_length=255, required=False, allow_blank=True)

    @transaction.atomic
    def create(self, validated_data):
        # 1. 提取 university_id 并查询对应的 University 实例
        university_id = validated_data.pop('university_id')  # 从validated_data中移除，避免后续解包干扰
        university_instance = University.objects.get(id=university_id)  # 正确的get调用：关键字参数id

        # 2. 先创建用户
        _user, _data = create_user_by_validated_data(validated_data,
                                                     user_type=constants.UserDict.USER_TYPE_TEACHER)  # 固定教师角色

        # 3. 再创建教师
        teacher = Teacher.objects.create(
            user=_user,
            university=university_instance,
            **_data,
        )
        return teacher


class TeacherFlatUpdateSerializer(serializers.ModelSerializer):
    # 把 user 表字段“平铺”到顶层
    nickname = serializers.CharField(required=False, allow_blank=False)
    name = serializers.CharField(required=False, allow_blank=False)
    phone = serializers.CharField(required=False, allow_blank=False)
    email = serializers.CharField(required=False, allow_blank=False)

    class Meta:
        model = Teacher
        fields = (
            'university_id', 'subject', 'professional_title', 'profession', 'department',
            'nickname', 'name', 'phone', 'email'
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        # 1. 更新用户信息
        _user, _data = update_user_by_validated_data(instance.user, validated_data)

        # 2. 更新教师
        for k, v in validated_data.items():
            if k == 'user':
                setattr(instance, k, _user)
            else:
                setattr(instance, k, v)
        instance.save()
        return instance
