import django.conf
from django.contrib.admin.templatetags.admin_list import pagination
from rest_framework.decorators import api_view

from AAServer import constants
from AAServer.common.middleware import GlobalRequestMiddleware
from AAServer.common.pagination import CwsPageNumberPagination
from AAServer.response import R, ResponseEnum
from AAServer.utils.SessionUtils import SessionUtils
from apps.resource.models import Resource
from apps.resource.serializers import ResourceUpdateSerializer, ResourceSerializer

# Create your views here.

ENDPOINT = django.conf.settings.MINIO_ENDPOINT
USE_HTTPS = django.conf.settings.MINIO_USE_HTTPS


@api_view(['POST'])
def upload_resource(request):
    """
    上传或获取资源
    :param request:
    :return:
    """
    # 处理上传资源的逻辑
    # 这里可以使用ResourceSerializer来序列化上传的数据
    rs = ResourceSerializer(data=request.data)
    if rs.is_valid():
        file = rs.validated_data['file']  # 2025-8-12/3489700_20250616190501_1_TdFsQoq.png
        instance = rs.save(size=file.size if file else None,
                old_filename=str(file),
                sequence=rs.validated_data['sequence'] if 'sequence' in rs.validated_data else 1)
        return R.success(data=ResourceSerializer(instance).data)
    return R.fail(ResponseEnum.UPLOAD_FAIL, data=rs.errors)

@api_view(['GET'])
def get_resource(request, id):
    """
    获取资源
    :param request:
    :param id: 资源ID
    :return:
    """
    try:
        resource = ResourceSerializer(instance=Resource.objects.get(id=id))
        return R.success(data=resource.data)
    except Resource.DoesNotExist:
        return R.fail(ResponseEnum.RESOURCE_NOT_FOUND, data={'id': id})


@api_view(['GET'])
def get_resources(request):
    """
    获取资源列表
    :param request:
    :return:
    """
    name = request.GET.get('name', '').strip()
    type_id = request.GET.get('type')

    qs = Resource.objects.all()
    if name:  # 只当 name 非空才过滤
        qs = qs.filter(name__icontains=name)
    if type_id:  # 只当 type 非空才过滤
        qs = qs.filter(type=type_id)

    qs = qs.order_by('update_time')

    paginator = CwsPageNumberPagination()
    page = paginator.paginate_queryset(qs, request)

    serializer = ResourceSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['PUT', 'DELETE'])
def update_or_delete_resource(request):
    """
    更新资源
    :param request:
    :return:
    """
    if request.method == 'PUT':
        _id = request.data.get('id')
        if not _id:
            return R.fail(ResponseEnum.PARAM_IS_BLANK, data={'id': 'ID is required'})

        resource = Resource.objects.get(id=_id)
        serializer = ResourceUpdateSerializer(resource, data=request.data, partial=True)  # 允许部分更新
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return R.success(data=ResourceUpdateSerializer(instance).data)
    elif request.method == 'DELETE':
        ids = request.GET.getlist('ids')
        if not ids:
            return R.fail(ResponseEnum.PARAM_IS_BLANK, data={'ids': 'IDs are required'})

        # TODO: 引用检查，后续完善

        Resource.objects.filter(id__in=ids).delete()
        return R.success(data={'deleted_ids': ids})
    return R.success(ResponseEnum.INVALID_METHOD)

@api_view(['GET'])
def get_resource_type(request):
    """
    获取资源类型
    :param request:
    :return:
    """
    return R.success(data=constants.ResourceDict.RESOURCE_TYPE)