#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
全局异常处理
@Project : AAServer 
@File    : exception_handler.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/6 14:14 
@Version : 1.0
"""
import logging
import traceback

import redis
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, ValidationError, NotFound
from rest_framework.views import exception_handler

from AAServer.common.exceptions import CustomException
from AAServer.response import ResponseEnum, R

logger = logging.getLogger("AAServer")


def common_exception_handler(exc, context):
    """
    通用异常处理
    :param exc:
    :param context:
    :return:
    """
    response = exception_handler(exc, context)
    request = context["request"]
    print('异常信息:', exc)
    traceback.print_exc()
    logger.error(
        "Request Basics:\n"
        f"  Path: {request.path}\n"
        f"  Method: {request.method}\n"
        f"  Host: {request.get_host()}"
    )

    # 处理自定义异常
    if isinstance(exc, AuthenticationFailed):
        return R.fail(ResponseEnum.INVALID_TOKEN, data=exc.detail)
    if isinstance(exc, NotAuthenticated):
        return R.fail(ResponseEnum.USER_NOT_LOGIN, data=exc.detail)
    if isinstance(exc, ValidationError):
        return R.fail(ResponseEnum.PARAM_IS_INVAlID, data=exc.detail)
    if isinstance(exc, redis.exceptions.RedisError):
        return R.fail(ResponseEnum.NETWORK_ERROR, data=str(exc))
    if isinstance(exc, NotFound):
        return R.fail(ResponseEnum.DATA_NOT_FOUND, data=str(exc))
    if isinstance(exc, CustomException):
        return R.fail_code_msg(exc.code, exc.detail)

    # 处理其他异常
    if response is not None:
        response = R.fail(ResponseEnum.SYSTEM_ERROR, data=response.data)
    else:
        response = R.fail(ResponseEnum.SYSTEM_ERROR)
    return response
