from rest_framework.decorators import api_view

from AAServer.response import R
from apps.university.models import University
from apps.university.serializers import UniversitySerializer


@api_view(['GET'])
def get_filtered_university_list(request):
    """
    获取检索过的学校列表
    :param request:
    :return:
    """
    keyword = request.GET.get('keyword', None)
    qs = University.objects.all()
    if keyword:
        print(keyword)
        qs = qs.filter(school_name__icontains=keyword)
    limited_queryset = qs[:20] # 仅查询前20条记录
    return R.success(UniversitySerializer(limited_queryset, many=True).data)