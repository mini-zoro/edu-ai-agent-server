from django.db import transaction
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from AAServer import redis_util
from AAServer.common.exceptions import CustomException, ValidationException
from AAServer.response import R
from AAServer.utils.RedisUtils import RedisUtil, CacheKeys
from apps import permission
from apps.auth.utils import clear_user_perms_cache
from apps.permission.models import Permission, PermissionRole
from apps.permission.serializers import PermissionSerializer, PermissionTreeSerializer
from apps.role.models import Role


class PermissionView(APIView):
    """
    权限管理视图
    """

    def get(self, request):
        """
        获取权限列表
        """
        return R.success(PermissionSerializer(Permission.objects.all(), many=True).data)

    @transaction.atomic
    def put(self, request):
        """
        更新角色权限
        """
        role_id = request.data['roleId']
        role = Role.objects.get(id=role_id)  # 确认角色存在
        if not role:
            raise ValidationException(detail='角色不存在')
        permission_ids = request.data.get('permissionIds', [])
        permissions = Permission.objects.filter(id__in=permission_ids)
        if len(permissions) != len(permission_ids):
            raise ValidationException(detail='部分权限不存在')
        # 删除旧角色权限关系
        PermissionRole.objects.filter(role=role).delete()
        # 创建新角色权限关系
        PermissionRole.objects.bulk_create([
            PermissionRole(permission=p, role=role) for p in permissions
        ], ignore_conflicts=True)

        clear_user_perms_cache(role_id=role_id)  # 清除拥有该角色的用户权限缓存

        return R.success()


@api_view(['GET'])
def get_permission_by_role(request, role_id):
    """
    根据角色ID获取权限列表
    """
    permissions = Permission.objects.filter(permissionrole__role_id=role_id).distinct()
    serializer = PermissionSerializer(permissions, many=True)
    return R.success(serializer.data)


@api_view(['GET'])
def get_permission_tree(request):
    """
    获取权限树
    """
    root_perms = redis_util.get_object(CacheKeys.PERMISSION_TREE)
    if root_perms:
        return R.success(root_perms)
    root_perms_qs = Permission.objects.filter(parent=None)
    root_perms = PermissionTreeSerializer(root_perms_qs, many=True).data
    redis_util.set_object(CacheKeys.PERMISSION_TREE, root_perms)
    return R.success(root_perms)
