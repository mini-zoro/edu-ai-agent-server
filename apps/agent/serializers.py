from rest_framework import serializers
from apps.agent.models import Agent, Conversation, Message, AgentTag, Tag
from apps.code_dict.models import Code
from apps.resource.serializers import ResourceSerializer


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'description', 'sequence')


class TagCreateSerializer(serializers.ModelSerializer):
    """标签创建序列化器"""
    class Meta:
        model = Tag
        fields = ('name', 'description', 'sequence')


class AgentSerializer(serializers.ModelSerializer):
    """
    智能体序列化器
    """
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Tag.objects.all(),
        required=False,
        source='tags'
    )
    avatar = ResourceSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Agent
        exclude = ('create_user', 'update_user',
                   'is_del', 'apikey', 'agent_type')

    def get_avatar_url(self, obj):
        if obj.avatar and obj.avatar.file:
            return obj.avatar.remote_file_url
        return None


class AgentCreateSerializer(serializers.ModelSerializer):
    """
    智能体创建序列化器
    """
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Tag.objects.all(),
        required=False,
        source='tags'
    )

    class Meta:
        model = Agent
        fields = ('name', 'description', 'avatar',
                  'baseurl', 'apikey', 'tag_ids', 'agent_type')


class AgentUpdateSerializer(serializers.ModelSerializer):
    """
    智能体更新序列化器
    """
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Tag.objects.all(),
        required=False,
        source='tags'
    )

    class Meta:
        model = Agent
        fields = ('name', 'description', 'avatar',
                  'baseurl', 'apikey', 'tag_ids', 'agent_type')


class ConversationSerializer(serializers.ModelSerializer):
    """
    对话序列化器
    """
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    agent_avatar = ResourceSerializer(source='agent.avatar', read_only=True)

    class Meta:
        model = Conversation
        exclude = ('create_user', 'update_user', 'is_del')

    def get_message_count(self, obj):
        return obj.messages.filter(is_del=0).count()

    def get_last_message(self, obj):
        last_msg = obj.messages.filter(
            is_del=0).order_by('-create_time').first()
        if last_msg:
            return {
                'content': last_msg.content[:100]+'...' if len(last_msg.content) > 100 else last_msg.content,
                'role': last_msg.role,
                'create_time': last_msg.create_time
            }
        return None


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    对话创建序列化器
    """
    agent_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Conversation
        fields = ('agent_id', 'title')

    def validate_agent_id(self, value):
        """验证智能体是否存在且用户有权限使用"""
        try:
            agent = Agent.objects.get(id=value, is_del=0)
        except Agent.DoesNotExist:
            raise serializers.ValidationError("智能体不存在")

        if not agent.can_used_by(self.context['request'].user):
            raise serializers.ValidationError("您没有权限使用此智能体")
        return value

    def create(self, validated_data):
        """创建对话"""
        agent_id = validated_data.pop('agent_id')
        agent = Agent.objects.get(id=agent_id)
        validated_data['agent'] = agent
        return super().create(validated_data)


class ConversationUpdateSerializer(serializers.ModelSerializer):
    """
    对话标题更新序列化器
    """
    class Meta:
        model = Conversation
        fields = ('title',)


class MessageSerializer(serializers.ModelSerializer):
    """
    消息序列化器
    """
    class Meta:
        model = Message
        exclude = ('create_user', 'update_user', 'is_del')


class ChatRequestSerializer(serializers.Serializer):
    """
    聊天请求序列化器
    """
    agent_id = serializers.IntegerField()
    query = serializers.CharField()
    conversation_id = serializers.CharField(required=False, allow_blank=True)
    auto_generate_name = serializers.BooleanField(default=True)

    def validate_agent_id(self, value):
        try:
            agent = Agent.objects.get(id=value, is_del=0)
        except Agent.DoesNotExist:
            raise serializers.ValidationError("智能体不存在")
        if not agent.can_used_by(self.context['request'].user):
            raise serializers.ValidationError("您没有权限使用此智能体")
        return value


class AgentTagSerializer(serializers.ModelSerializer):
    """
    智能体标签关联序列化器
    """
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    tag_name = serializers.CharField(source='tag.name', read_only=True)

    class Meta:
        model = AgentTag
        exclude = ('create_user', 'update_user', 'is_del')
