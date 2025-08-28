from rest_framework import permissions
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from AAServer import redis_util
from AAServer.common.authentication import get_authorization_token, generate_token
from AAServer.response import R, ResponseEnum
from AAServer.utils.RedisUtils import CacheKeys
from apps.auth.models import User
from apps.auth.services import do_login


@api_view(['POST'])
@authentication_classes(())
@permission_classes((permissions.AllowAny,))
def login(request):
    # 参数校验
    account = request.data['account']
    password = request.data['password']
    if not account or not password:
        return R.fail(ResponseEnum.PARAM_IS_BLANK)

    user = User.objects.get(account=account)
    if not user or not user.check_password(password):
        return R.fail(ResponseEnum.USER_LOGIN_ERROR)

    return R.success(do_login(user))


@api_view(['POST'])
def logout(request):
    redis_util.delete_value(CacheKeys.TOKEN_USER + str(request.headers.get('Authorization').split()[1]))
    return R.success()


@api_view(['GET'])
def refresh_token(request):
    token = get_authorization_token(request)
    if not token:
        return R.fail(ResponseEnum.USER_NOT_LOGIN)

    user_data = redis_util.get_value(CacheKeys.TOKEN_USER + str(token))
    if not user_data:
        return R.fail(ResponseEnum.INVALID_TOKEN)

    # 设置旧Token有效期为10秒
    redis_util.set_value(CacheKeys.TOKEN_USER + str(token), user_data, timeout=10)

    # 生成新的Token并更新缓存
    access_token = generate_token()
    redis_util.set_value(CacheKeys.TOKEN_USER + str(access_token), user_data, timeout=3600 * 24)
    return R.success({
        'token': access_token,
    })
