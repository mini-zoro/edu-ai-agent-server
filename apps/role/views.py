from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from AAServer.common.exceptions import CustomException
from AAServer.common.pagination import CwsPageNumberPagination
from AAServer.response import R, ResponseEnum
from apps.role.models import Role
from apps.role.serializers import RoleSerializer

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
        qs = Role.objects.all()

        paginator = CwsPageNumberPagination()
        page = paginator.paginate_queryset(qs, request)

        serializer = RoleSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """
           创建新角色
           """
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save(type = 2)  # 强制设置为用户自定义角色
        return R.success({
            'role_id': role.id,
        })

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
        return R.success()
