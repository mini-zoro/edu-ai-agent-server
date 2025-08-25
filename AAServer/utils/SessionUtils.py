#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : SessionUtils.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/7 14:58 
@Version : 1.0
"""
import threading

_thread_locals = threading.local()

class SessionUtils:

    @classmethod
    def get_current_user_id(cls):
        """工具函数：返回当前登录用户 id（未登录返回 None）"""
        user = getattr(_thread_locals, 'user', None)
        if user and user.is_authenticated:
            # 你的 User 主键是 BigInteger，这里直接返回
            return user.id
        return None

    @classmethod
    def get_current_user(cls):
        """获取当前登录用户对象"""
        user = getattr(_thread_locals, 'user', None)
        if user and user.is_authenticated:
            return user
        return None