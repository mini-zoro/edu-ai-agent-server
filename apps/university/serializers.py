#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : serializers.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/9/2 22:07 
@Version : 1.0
"""
from rest_framework import serializers

from apps.university.models import University

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        exclude = ('create_user', 'update_user', 'is_del', 'create_time', 'update_time')

class UniversityInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        exclude = ('create_user', 'update_user', 'is_del')