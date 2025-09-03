#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : initroles.py.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/9/1 16:00 
@Version : 1.0
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.rbac.constants import DEFAULT_PERMS, ROLE_OBJ


class Command(BaseCommand):
    help = '初始化系统默认角色和权限'

    @transaction.atomic
    def handle(self, *args, **options):
        from apps.role.models import Role
        from apps.permission.models import Permission

        # 遍历系统预设角色
        for role_key, perms in DEFAULT_PERMS.items():
            # 检查角色是否存在，不存在则创建
            exists = Role.objects.filter(role_key=role_key).exists()
            if exists:
                role = Role.objects.get(role_key=role_key)
            else:
                role = ROLE_OBJ.get(role_key).save()

            # TODO 添加角色默认权限

        self.stdout.write(self.style.SUCCESS('默认角色初始化完成'))
