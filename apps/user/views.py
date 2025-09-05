from django.core.cache import cache
from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework.decorators import api_view

from AAServer import redis_util
from AAServer.common.authentication import get_authorization_token
from AAServer.common.cache import cache_get, cache_set
from AAServer.common.pagination import CwsPageNumberPagination
from AAServer.response import R, ResponseEnum
from AAServer.utils.RedisUtils import CacheKeys
from apps.auth.models import User
from apps.user.serializers import UserSerializer, UserSessionSerializer, UserInlineSerializer, UserWithRolesSerializer


@api_view(['GET'])
def get_user_info(request):
    """
    获取用户信息
    :param request: 请求对象
    :return: 用户信息
    """
    cache_key = CacheKeys.TOKEN_USER + get_authorization_token(request)
    # user_dict = cache_get(cache_key)
    user_data = redis_util.get_object(cache_key)
    if not user_data:
        user_data = UserSessionSerializer(User.objects.get(id=request.user.id)).data
        redis_util.set_object(cache_key, user_data)
    return R.success(user_data)

@api_view(['GET'])
def get_user_by_type(request):
    """
    根据用户类型分页获取用户列表
    :param request: 请求对象
    :return: 用户列表
    """
    user_type = request.GET.get('type', None)
    if not user_type:
        return R.fail(ResponseEnum.PARAM_IS_INVAlID)
    qs = User.objects.filter(type=user_type).order_by('-create_time')

    paginator = CwsPageNumberPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = UserWithRolesSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)