#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : permissions.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/9/1 16:34 
@Version : 1.0
"""
from rest_framework.permissions import BasePermission

from apps.auth.utils import get_user_perms_to_array
from apps.rbac.constants import PERMISSION_KEY


class RBACPermission(BasePermission):
    def has_permission(self, request, view):
        perm_key = request.resolver_match.kwargs.get(PERMISSION_KEY, None)
        if not perm_key:
            return True
        route_key = f"api:{perm_key}:{request.method.lower()}"
        print(route_key)
        return route_key in get_user_perms_to_array(request.user)
