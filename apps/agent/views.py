from django.shortcuts import render
import json
import uuid
from django.db import transaction
from django.db.models import Q, F
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from AAServer.common.pagination import CwsPageNumberPagination
from AAServer.response import R, ResponseEnum
from apps.agent.models import Agent, Conversation, Message, AgentTag, Tag
from apps.agent.serializers import (
    AgentSerializer, AgentCreateSerializer, AgentUpdateSerializer,
    ConversationSerializer, ConversationCreateSerializer, MessageSerializer,
    ChatRequestSerializer, AgentTagSerializer, TagSerializer, TagCreateSerializer
)
from apps.agent.services import DifyService, ConversationService
from AAServer.common.exceptions import CustomException, ValidationException
# Create your views here.


class AgentView(APIView):
    """
    智能体查看视图 - 管理员、教师、学生都可以访问
    """

    def _filter_agents_by_user_permission(self, queryset, user):
        """
        根据用户权限过滤智能体
        """
        if user.type == 0:  # 管理员
            return queryset
        elif user.type == 1:  # 教师
            return queryset.filter(Q(agent_type=1) | Q(agent_type=0))
        else:  # 学生
            return queryset.filter(Q(agent_type=2) | Q(agent_type=0))

    def get(self, request, **kwargs):
        """
        获取智能体列表(支持标签和搜索过滤)
        """
        # 1. 获取查询参数
        search = request.GET.get('search', '').strip()
        tag_ids = request.GET.getlist('tag_ids', '')
        # 2. 构建基础查询集
        queryset = Agent.objects.filter(is_del=False)
        # 3. 根据用户权限过滤智能体
        queryset = self._filter_agents_by_user_permission(
            queryset, request.user)
        # 4. 搜索过滤
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        # 5. 标签过滤
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        # 6. 排序
        queryset = queryset.order_by('-create_time')
        # 7. 分页
        paginator = CwsPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = AgentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class AgentManageView(APIView):
    """
    智能体管理视图 - 仅管理员可以访问
    """

    def _filter_agents_by_user_permission(self, queryset, user):
        """
        根据用户权限过滤智能体
        """
        if user.type == 0:  # 管理员
            return queryset
        elif user.type == 1:  # 教师
            return queryset.filter(Q(agent_type=1) | Q(agent_type=0))
        else:  # 学生
            return queryset.filter(Q(agent_type=2) | Q(agent_type=0))

    def get(self, request, **kwargs):
        """
        获取智能体列表(支持标签和搜索过滤)
        """
        # 1. 获取查询参数
        search = request.GET.get('search', '').strip()
        tag_ids = request.GET.getlist('tag_ids', '')
        # 2. 构建基础查询集
        queryset = Agent.objects.filter(is_del=False)
        # 3. 根据用户权限过滤智能体
        queryset = self._filter_agents_by_user_permission(
            queryset, request.user)
        # 4. 搜索过滤
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        # 5. 标签过滤
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        # 6. 排序
        queryset = queryset.order_by('-create_time')
        # 7. 分页
        paginator = CwsPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = AgentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, **kwargs):
        """
        创建智能体（仅管理员）
        """
        serializer = AgentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agent = serializer.save()
        return R.success({
            'agent_id': agent.id,
            'message': '智能体创建成功'
        })

    def put(self, request, **kwargs):
        """
        更新智能体（仅管理员）
        """
        agent_id = request.data.get('agent_id')
        if not agent_id:
            return R.fail(ResponseEnum.PARAM_IS_BLANK)
        try:
            agent = Agent.objects.get(id=agent_id, is_del=False)
        except Agent.DoesNotExist:
            raise CustomException(
                code=301, detail=f"智能体(ID:{agent_id})不存在或已删除")

        serializer = AgentUpdateSerializer(
            instance=agent, data=request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationException(detail=serializer.errors)
        try:
            with transaction.atomic():
                serializer.save()
        except Exception as e:
            raise CustomException(code=302, detail=f"更新智能体失败: {str(e)}")
        return R.success({
            'agent_id': agent_id,
            'message': '智能体更新成功'
        })

    def delete(self, request, **kwargs):
        """
        删除智能体（仅管理员）
        """
        agent_id = request.data.get('agent_id')
        if not agent_id:
            return R.fail(ResponseEnum.PARAM_IS_BLANK, "智能体ID不能为空")
        try:
            agent = Agent.objects.get(id=agent_id, is_del=False)
        except Agent.DoesNotExist:
            return R.fail(ResponseEnum.DATA_NOT_FOUND, f"智能体(ID:{agent_id})不存在或已删除")

        Agent.objects.filter(id=agent_id).update(is_del=1)
        return R.success({
            'agent_id': agent_id,
            'message': '智能体删除成功'
        })


class AgentDetailView(APIView):
    """
    智能体详情视图 - 管理员、教师、学生都可以访问
    """

    def get(self, request, agent_id):
        """
        获取智能体详情
        """
        try:
            agent = Agent.objects.get(id=agent_id, is_del=False)
        except Agent.DoesNotExist:
            return R.fail(ResponseEnum.PARAM_IS_BLANK)
        if not agent.can_used_by(request.user):
            return R.fail(ResponseEnum.NOT_PERMISSION, "您没有权限使用此智能体")
        serializer = AgentSerializer(agent)
        return R.success(serializer.data)


class TagView(APIView):
    """
    标签查看视图 - 管理员、教师、学生都可以访问
    """

    def get(self, request, **kwargs):
        """
        获取标签列表"""
        tags = Tag.objects.filter(is_del=False).order_by('sequence', 'name')
        serializer = TagSerializer(tags, many=True)
        return R.success(serializer.data)


class TagManageView(APIView):
    """
    标签管理视图 - 仅管理员可以访问
    """

    def get(self, request, **kwargs):
        """
        获取标签列表"""
        tags = Tag.objects.filter(is_del=False).order_by('sequence', 'name')
        serializer = TagSerializer(tags, many=True)
        return R.success(serializer.data)

    def post(self, request, **kwargs):
        """
        创建标签（仅管理员）
        """
        serializer = TagCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag = serializer.save()
        return R.success({
            'tag_id': tag.id,
            'message': '标签创建成功'
        })

    def delete(self, request, **kwargs):
        """
        删除标签（仅管理员）
        """
        tag_id = request.data.get('tag_id')
        if not tag_id:
            return R.fail(ResponseEnum.PARAM_IS_BLANK, "标签ID不能为空")
        try:
            tag = Tag.objects.get(id=tag_id, is_del=False)
        except Tag.DoesNotExist:
            return R.fail(ResponseEnum.DATA_NOT_FOUND, f"标签(ID:{tag_id})不存在或已删除")

        Tag.objects.filter(id=tag_id).update(is_del=1)
        return R.success({
            'tag_id': tag_id,
            'message': '标签删除成功'
        })
