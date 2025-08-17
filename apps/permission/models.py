from django.db import models

from AAServer.common.models import BaseModel
from apps.auth.models import User


# Create your models here.

class Permission(BaseModel):
    id = models.BigIntegerField(primary_key=True, db_comment='权限ID')
    parent = models.ForeignKey(
        'self',  # 自引用外键
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        db_column='parent_id',  # 数据库列名仍叫 parent_id
        related_name='children',  # 反向查询：perm.children.all()
        db_comment='父级权限'
    )
    key = models.CharField(max_length=255, blank=True, null=True, db_comment='权限码（权限路径）')
    type = models.IntegerField(blank=True, null=True, db_comment='权限类型，0表示页面权限，1表示操作权限')
    name = models.CharField(max_length=255, blank=True, null=True, db_comment='权限名')
    grade = models.IntegerField(blank=True, null=True, db_comment='目录层级')
    des = models.CharField(max_length=255, blank=True, null=True, db_comment='描述')

    class Meta:
        db_table = 'sys_permission'
        db_table_comment = '权限表'


class Role(BaseModel):
    id = models.BigIntegerField(primary_key=True, db_comment='角色ID')
    role_key = models.CharField(max_length=255, blank=True, null=True, db_comment='角色码')
    role_name = models.CharField(max_length=255, blank=True, null=True, db_comment='角色名称')
    des = models.CharField(max_length=255, blank=True, null=True, db_comment='描述')
    type = models.IntegerField(blank=True, null=True, db_comment='角色类型，0可选，1特殊，2用户自定义')

    class Meta:
        db_table = 'sys_role'
        db_table_comment = '角色表'

class PermissionRole(BaseModel):
    id = models.BigIntegerField(primary_key=True, db_comment='ID')
    permission = models.ForeignKey(Permission, db_comment='外键，sys_permission权限ID', on_delete=models.RESTRICT, db_column='permission_id')
    role = models.ForeignKey(Role, db_comment='外键，sys_role角色ID', on_delete=models.RESTRICT, db_column='role_id')

    class Meta:
        db_table = 'sys_permission_role'
        db_table_comment = '权限角色表'


class UserRole(BaseModel):
    id = models.BigIntegerField(primary_key=True, db_comment='ID')
    user = models.ForeignKey(User, db_comment='外键，sys_user用户ID', on_delete=models.RESTRICT, db_column='user_id')
    role = models.ForeignKey(Role, db_comment='外键，sys_role角色ID', on_delete=models.RESTRICT, db_column='role_id')

    class Meta:
        db_table = 'sys_user_role'
        db_table_comment = '用户角色关联表'