#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : services.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/9/1 02:54 
@Version : 1.0
"""


def get_roles_by_user_id(user_id):
    """
    根据用户ID获取角色列表
    逻辑删除的用户角色关系不包含在内
    :param user_id: 用户ID
    :return: 角色列表
    """
    from apps.role.models import Role

    roles = Role.objects.filter(userrole__user_id=user_id, userrole__is_del=0).distinct()
    return roles
