#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
通用模型
@Project : AAServer 
@File    : models.py
@IDE     : PyCharm 
@Author  : Guqier
@Date    : 2025/8/6 18:10 
@Version : 1.0
"""
from django.db import models
from django.utils import timezone

from AAServer.common.manager import ModelManager
from AAServer.common.middleware import GlobalRequestMiddleware
from AAServer.utils.SessionUtils import SessionUtils
from AAServer.common.snowflake import next_id


class LogicalDeleteModel(models.Model):
    objects = ModelManager()

    is_del = models.IntegerField(db_column='del', blank=True, null=True,
                                    db_comment='逻辑删除，0启用，1停用')  # Field renamed because it was a Python reserved word.
    class Meta:
        abstract = True
    def save(self, *args, **kwargs):
        self.is_del = 0
        super().save(*args, **kwargs)

class BaseModel(LogicalDeleteModel):
    """
    模型基类，除“SYS_”表以外的所有业务表必须继承
    """
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    create_user = models.BigIntegerField(blank=True, null=True, db_comment='创建用户')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')
    update_user = models.BigIntegerField(blank=True, null=True, db_comment='更新用户')

    class Meta:
        abstract = True


    def save(self, *args, **kwargs):
        now = timezone.now()
        # user_id = SessionUtils.get_current_user_id()
        user = GlobalRequestMiddleware.get_user()  # 获取当前用户对象
        user_id = None
        if user is not None:
            user_id = GlobalRequestMiddleware.get_user().id # 获取当前用户ID

        # 新增
        if self._state.adding:
            self.id = next_id()
            if hasattr(self, 'create_time'):
                self.create_time = self.create_time or now
            if hasattr(self, 'create_user'):
                self.create_user = self.create_user or user_id
        # 更新
        if hasattr(self, 'update_time'):
            self.update_time = now
        if hasattr(self, 'update_user'):
            self.update_user = user_id

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        逻辑删除
        """
        self.is_del = 1
        self.save(update_fields=['is_del'])