#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : AAServer 
@File    : addperm.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/9/1 17:51 
@Version : 1.0
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from AAServer import redis_util
from AAServer.utils.RedisUtils import CacheKeys
from apps.rbac.utils import clear_perms_cache


class Command(BaseCommand):
    help = '添加单个权限'

    def add_arguments(self, parser):
        parser.add_argument('--key', required=True, help='权限码，如 article.delete')
        parser.add_argument('--name', required=True, help='权限名称')
        parser.add_argument('--type', type=int, choices=[0, 1, 2], required=True,
                            help='权限类型：0 页面 1 接口 2 按钮')
        parser.add_argument('--parent', default=None,
                            help='父权限 key 或 id；无父级可省略')
        parser.add_argument('--des', default='', help='描述')

    @transaction.atomic
    def handle(self, *args, **options):
        from apps.permission.models import Permission

        key = options['key']
        name = options['name']
        ptype = options['type']
        des = options['des']

        # 检查权限是否存在
        if Permission.objects.filter(key=key).exists():
            raise CommandError(f'权限码：{key} 已存在')

        # 处理父级
        parent_obj = None
        parent_val = options['parent']
        if parent_val:
            try:
                parent_obj = Permission.objects.get(
                    key=parent_val
                ) if not str(parent_val).isdigit() else Permission.objects.get(
                    id=parent_val
                )
            except Permission.DoesNotExist:
                raise CommandError(f'父权限不存在：{parent_val}')

        # 创建/更新
        perm, created = Permission.objects.update_or_create(
            key=key,
            defaults={
                'name': name,
                'type': ptype,
                'grade': parent_obj.grade + 1 if parent_obj else 0,
                'parent': parent_obj,
                'des': des,
            }
        )
        action = '已创建' if created else '已更新'
        self.stdout.write(
            self.style.SUCCESS(f"{action} 权限：{key} -> {name}")
        )

        # 清除缓存
        clear_perms_cache()
