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
        tag_ids = request.GET.getlist('tag_ids', [])
        tag_ids = [tag_id for tag_id in tag_ids if tag_id and tag_id.strip()]
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
        tag_ids = request.GET.getlist('tag_ids', [])
        tag_ids = [tag_id for tag_id in tag_ids if tag_id and tag_id.strip()]
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
        agent_id = request.GET.get('agent_id')
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
        tag_id = request.GET.get('tag_id')
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


class ConversationView(APIView):
    """
    对话视图
    """

    def get(self, request, **kwargs):
        """
        获取用户的对话列表
        """
        queryset = Conversation.objects.filter(
            is_del=0, user_id=request.user.id)
        queryset = queryset.order_by('-update_time')
        paginator = CwsPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ConversationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, **kwargs):
        """
        创建对话
        """
        serializer = ConversationCreateSerializer(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save(user_id=request.user.id)
        return R.success({
            'conversation_id': conversation.id,
            'message': '对话创建成功'
        })

    def put(self, request, **kwargs):
        """
        更新对话标题
        """
        conversation_id = request.data.get('conversation_id')
        title = request.data.get('title')
        if not conversation_id:
            return R.fail(ResponseEnum.PARAM_IS_BLANK, "对话ID不能为空")
        if not title:
            return R.fail(ResponseEnum.PARAM_IS_BLANK, "标题不能为空")
        conversation = ConversationService.update_conversation_title(
            conversation_id=conversation_id,
            user_id=request.user.id,
            title=title)
        if not conversation:
            return R.fail(ResponseEnum.DATA_NOT_FOUND, "对话不存在")
        return R.success({
            'conversation_id': conversation_id,
            'message': '对话标题更新成功'
        })

    def delete(self, request, **kwargs):
        """
        删除对话
        """
        conversation_id = request.GET.get('conversation_id')
        if not conversation_id:
            return R.fail(ResponseEnum.PARAM_IS_BLANK, "对话ID不能为空")
        success = ConversationService.delete_conversation(
            conversation_id, request.user.id)
        if not success:
            return R.fail(ResponseEnum.DATA_NOT_FOUND, "对话不存在")
        return R.success({
            'conversation_id': conversation_id,
            'message': '对话删除成功'
        })


class MessageView(APIView):
    """
    消息视图
    """

    def get(self, request, **kwargs):
        """
        获取消息列表
        """

        conversation_id = request.GET.get('conversation_id')
        if not conversation_id:
            return R.fail(ResponseEnum.PARAM_IS_BLANK, "对话ID不能为空")
        messages = ConversationService.get_conversation_messgaes(
            conversation_id, request.user.id)
        if messages is None:
            return R.fail(ResponseEnum.DATA_NOT_FOUND, "对话不存在")
        serializer = MessageSerializer(messages, many=True)
        return R.success(serializer.data)


class ChatView(APIView):
    """
    聊天视图(流式响应)
    """

    def post(self, request, **kwargs):
        """
        发送消息
        """
        serializer = ChatRequestSerializer(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)

        agent_id = serializer.validated_data['agent_id']
        query = serializer.validated_data['query']
        conversation_id = serializer.validated_data['conversation_id']
        auto_generate_name = serializer.validated_data['auto_generate_name']

        try:
            agent = Agent.objects.get(id=agent_id, is_del=0)
        except Agent.DoesNotExist:
            return R.fail(ResponseEnum.DATA_NOT_FOUND, "智能体不存在")
        if not agent.can_used_by(request.user):
            return R.fail(ResponseEnum.NOT_PERMISSION, "您没有权限使用此智能体")
        conversation = None
        is_new_conversation = False
        if conversation_id:
            conversation = Conversation.objects.get(
                id=conversation_id, is_del=0, user_id=request.user.id)
        else:
            conversation = ConversationService.create_conversation(
                agent_id, request.user.id, "新对话"
            )
            is_new_conversation = True
        # 保存用户消息
        user_message_id = str(uuid.uuid4())
        ConversationService.save_message(
            conversation, user_message_id, "user", query)
        # 调用Dify API
        try:
            dify_response = DifyService.chat_with_agent(
                agent, query, conversation.conversation_id, request.user.id, auto_generate_name)
        except Exception as e:
            return R.fail(ResponseEnum.SYSTEM_ERROR, str(e))
        # 新对话，更新智能体使用人数
        if is_new_conversation:
            ConversationService.update_agent_usage(agent_id)

        def generate_response():
            for data in DifyService.parse_dify_response(dify_response):
                if data.get('event') == 'message':
                    # 消息内容
                    assistant_content += data.get('answer', '')
                    yield f"data:{json.dumps({'type': 'message', 'content': data.get('answer', '')})}\n\n"
                    break
                elif data.get('event') == 'message_end':
                    # 消息结束
                    break
        return StreamingHttpResponse(generate_response(), content_type='text/event-stream')

        return StreamingHttpResponse(generate_response(), content_type='text/event-stream')
