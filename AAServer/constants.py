#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
应用全局常量
@Project : AAServer 
@File    : constants.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/13 13:03 
@Version : 1.0
"""
class CodeDict:
    CODE_TEACHER_PROFESSION = 'teacher_profession' # 教师职业
    CODE_STUDENT_IDENTITY = 'student_identity' # 学生身份
    CODE_TEACHER_TITLE = 'teacher_title' # 教师职称
    STUDENT_STATUS = 'student_status' # 学生状态
    CODE_TYPE = [
        {
            'name': '教师职业',
            'type': CODE_TEACHER_PROFESSION
        },
        {
            'name': '学生身份',
            'type': CODE_STUDENT_IDENTITY
        },
        {
            'name': '教师职称',
            'type': CODE_TEACHER_TITLE
        },
        {
            'name': '学生状态',
            'type': STUDENT_STATUS
        }
    ]

class ResourceDict:
    """
    资源相关常量
    type < 0 为系统内置资源，用户不可修改
    """
    RESOURCE_TYPE = [
        {
            'name': '用户头像（系统）',
            'type': -1
        },
        {
            'name': '图片资源',
            'type': 0
        },
        {
            'name': '文档资源',
            'type': 1
        },
        {
            'name': '视频资源',
            'type': 2
        },
        {
            'name': '音频资源',
            'type': 3
        },
        {
            'name': '代码资源',
            'type': 4
        },
        {
            'name': '其他资源',
            'type': 5
        }
    ]

class UserDict:
    """
    用户相关常量
    """
    USER_TYPE_ADMIN   = 0  # 管理员
    USER_TYPE_TEACHER = 1  # 教师
    USER_TYPE_STUDENT = 2  # 学生

    # 用户密码校验正则表达式：包含8-20个字符且包含至少一个字母和一个数字
    USER_PASSWORD_REGEX = r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d!@#$%^&*()_+={}\[\]:;"\'<>,.?/\\|-]{8,20}$'

class RoleDict:
    """
    角色相关常量
    """
    ROLE_TYPE_OPTIONAL = 0  # 可选角色
    ROLE_TYPE_SYSTEM   = 1  # 系统角色
    ROLE_TYPE_CUSTOM   = 2  # 用户自定义角色