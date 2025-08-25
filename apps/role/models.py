from django.db import models

from AAServer.common.models import BaseModel
from apps.auth.models import User


class Role(BaseModel):
    id = models.BigIntegerField(primary_key=True, db_comment='角色ID')
    role_key = models.CharField(max_length=255, blank=True, null=True, db_comment='角色码')
    role_name = models.CharField(max_length=255, blank=True, null=True, db_comment='角色名称')
    des = models.CharField(max_length=255, blank=True, null=True, db_comment='描述')
    type = models.IntegerField(blank=True, null=True, db_comment='角色类型，0可选，1特殊，2用户自定义')

    class Meta:
        db_table = 'sys_role'
        db_table_comment = '角色表'
        ordering = ['-create_time']


class UserRole(BaseModel):
    id = models.BigIntegerField(primary_key=True, db_comment='ID')
    user = models.ForeignKey(User, db_comment='外键，sys_user用户ID', on_delete=models.RESTRICT, db_column='user_id')
    role = models.ForeignKey(Role, db_comment='外键，sys_role角色ID', on_delete=models.RESTRICT, db_column='role_id')

    class Meta:
        db_table = 'sys_user_role'
        db_table_comment = '用户角色关联表'