#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : exceptions.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/11 14:22 
@Version : 1.0
"""
from rest_framework import status
from rest_framework.exceptions import APIException


class CustomException(APIException):
    status_code = status.HTTP_200_OK  # 统一返回 400，前端按 code 处理
    default_detail = '网络异常'
    default_code = 999

    def __init__(self, code=None, detail=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code


class ValidationException(CustomException):
    default_detail = '数据校验异常'
    default_code = 101