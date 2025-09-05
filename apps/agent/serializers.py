from rest_framework import serializers
from apps.agent.models import Agent, Conversation, Message, AgentTag, Tag
from apps.code_dict.models import Code


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

    class Meta:
        model = Agent
        exclude = ('create_user', 'update_user', 'is_del', 'apikey', 'agent_type')


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
                  'baseurl', 'apikey', 'tag_ids', 'agent_type' )


class ConversationSerializer(serializers.ModelSerializer):
    """
    对话序列化器
    """
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        exclude = ('create_user', 'update_user', 'is_del')

    def get_message_count(self, obj):
        return obj.message_set.count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    对话创建序列化器
    """
    class Meta:
        model = Conversation
        fields = ('agent', 'title')


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


class ConversationUpdateSerializer(serializers.ModelSerializer):
    """
    对话标题更新序列化器
    """
    title = serializers.CharField(max_length=255)


class AgentTagSerializer(serializers.ModelSerializer):
    """
    智能体标签关联序列化器
    """
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    tag_name = serializers.CharField(source='tag.name', read_only=True)

    class Meta:
        model = AgentTag
        exclude = ('create_user', 'update_user', 'is_del')
