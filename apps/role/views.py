from django.db import transaction
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from AAServer.common.exceptions import CustomException
from AAServer.common.pagination import CwsPageNumberPagination
from AAServer.response import R, ResponseEnum
from apps.permission.models import PermissionRole
from apps.role.models import Role, UserRole
from apps.role.serializers import RoleSerializer
from apps.role.services import get_roles_by_user_id


@api_view(['GET'])
def get_all_roles(request):
    """
    获取所有角色列表
    """
    qs = Role.objects.all().order_by('-create_time')
    serializer = RoleSerializer(qs, many=True)
    return R.success(serializer.data)


class RoleMngView(APIView):
    """
    角色管理视图
    """

    def get(self, request):
        """
        分页获取角色列表
        """
        _role_name = request.GET.get('role_name', None)
        _role_key = request.GET.get('role_key', None)
        _type = request.GET.get('type', None)

        qs = Role.objects.all()
        if _role_name is not None:
            qs = qs.filter(role_name__icontains=_role_name)
        if _role_key is not None:
            qs = qs.filter(role_key__icontains=_role_key)
        if _type is not None and _type != '':
            qs = qs.filter(type=_type)
        qs = qs.order_by('-create_time')

        paginator = CwsPageNumberPagination()
        page = paginator.paginate_queryset(qs, request)

        serializer = RoleSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def post(self, request):
        """
           创建新角色
           """
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save(type=2)  # 强制设置为用户自定义角色
        return R.success({
            'role_id': role.id,
        })

    @transaction.atomic
    def put(self, request):
        """
            更新角色信息
            """
        role_id = request.data['id']
        role = Role.objects.get(id=role_id)
        if not role:
            return R.fail(ResponseEnum.PARAM_IS_INVAlID)
        if role.type != 2:
            raise CustomException(detail="系统角色不可修改")

        serializer = RoleSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return R.success()

    @transaction.atomic
    def delete(self, request):
        """
            删除角色（逻辑删除）
            """
        ids = request.GET.getlist('ids')
        if not ids:
            return R.fail(ResponseEnum.PARAM_IS_BLANK)
        qs = Role.objects.filter(id__in=ids).filter(type=2)
        count = qs.count()
        if count == 0:
            return R.fail(ResponseEnum.DATA_NOT_FOUND)
        for obj in qs:
            if obj.type != 2:
                return R.fail(ResponseEnum.PARAM_IS_INVAlID, f"角色 {obj.role_name} 不可删除")
        qs.delete()
        # 删除角色后续处理
        # 删除用户角色关系
        UserRole.objects.filter(role__id__in=ids).delete()
        # 删除角色权限关系
        PermissionRole.objects.filter(role__id__in=ids).delete()
        return R.success()


class UserRoleMngView(APIView):
    """
    用户角色管理视图
    """

    def get(self, request):
        """
        获取用户角色列表
        """
        user_id = request.GET.get('userId')
        roles = get_roles_by_user_id(user_id)
        serializer = RoleSerializer(roles, many=True)
        return R.success(serializer.data)

    @transaction.atomic
    def put(self, request):
        """
        更新用户角色
        """
        user_id = request.data['userId']
        role_ids = request.data.get('roleIds', [])
        roles = Role.objects.filter(id__in=role_ids)
        if len(roles) != len(role_ids):
            return R.fail(ResponseEnum.PARAM_IS_INVAlID, "部分角色不存在")
        # 删除旧用户角色关系
        UserRole.objects.filter(user_id=user_id).delete()
        # 创建新用户角色关系
        if len(roles) == 0:
            return R.success()
        user_roles = [UserRole(user_id=user_id, role=role) for role in roles]
        for ur in user_roles:
            ur.save()
        return R.success()
