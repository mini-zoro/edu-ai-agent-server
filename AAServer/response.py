#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
通用响应封装
@Project : AAServer
@File    : response.py
@IDE     : PyCharm
@Author  : Guqier
@Date    : 2025/8/6 13:59
@Version : 1.0
"""
from enum import Enum

from rest_framework.response import Response
from rest_framework import status


class CodeMsg:
    code = 1
    msg = 'success'

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return f'code: {self.code}, msg: {self.msg}'


class ResponseEnum(Enum):
    """
    通用状态码
    """
    SUCCESS = (1, "success")
    ERROR = (0, "error")

    """
    业务错误状态码
    """
    PARAM_IS_INVAlID = (101, "参数无效")

    PARAM_IS_BLANK = (102, "必要参数为空")

    """
    用户错误
    201 - 299
    """
    USER_NOT_LOGIN = (201, "用户未登录")
    INVALID_TOKEN = (202, "无效Token信息")
    USER_NOT_EXIST = (203, "用户不存在")
    USER_LOGIN_ERROR = (204, "登陆失败，账号或者密码有误")
    PERMISSION_DENIED = (205, "当前用户无权限访问")
    TOKEN_EXPIRED = (206, "Token已过期")
    NOT_FOR_STUDENT = (207, "管理后台仅限教师或管理员登录")
    ERROR_AUTH_CODE = (208, "验证码错误")
    WX_ERROR = (209, "微信验证错误")
    CODE_EMPTY = (210, "CODE不存在")
    WX_USER_NEED_BIND = (211, "未绑定账号")
    WX_USER_BIND_ERROR = (212, "绑定账号失败")

    """
    业务错误
    301 - 399 
    """
    DATA_NOT_FOUND = (301, "没有数据")
    HANDLE_FAIL = (302, "业务处理失败")

    DATABASE_OPERATION_FAIL = (303, "数据库操作失败")
    UPLOAD_FAIL = (304, "文件上传失败")
    DAILY_ALREADY_FINISHED = (305, "每日一练已完成")
    GROUP_JOIN_COUNT_MAX = (306, "加入小组数已最大")
    GROUP_INVITATION_CODE_INVALID = (307, "邀请码不存在或已过期")
    TEST_PAPER_INVALID = (308, "试卷不存在或已删除")

    RESOURCE_NOT_FOUND = (309, "资源不存在或已删除")
    SYSTEM_ERROR = (999, "系统异常")

    """
    数据错误
    """
    CACHE_NOT_EXIST = (401, "缓存不存在或已过期")
    INVALID_METHOD = (402, "请求方法不允许")

    """
    第三方服务异常
    """
    NETWORK_ERROR = (501, "网络异常")
    REDIS_TIMEOUT = (502, "Redis服务超时")


    @property
    def code(self):
        """获取状态码"""
        return self.value[0]

    @property
    def msg(self):
        """获取状态码信息"""
        return self.value[1]


class R:

    @staticmethod
    def success(data=None):
        return Response({'code': ResponseEnum.SUCCESS.code, 'msg': ResponseEnum.SUCCESS.msg, 'data': data},
                        status=status.HTTP_200_OK)

    @staticmethod
    def fail(code_msg, data=None):
        return Response({'code': code_msg.code, 'msg': code_msg.msg, 'data': data}, status=status.HTTP_200_OK)

    @staticmethod
    def fail_code_msg(code, msg, data=None):
        return Response({'code': code, 'msg': msg, 'data': data}, status=status.HTTP_200_OK)