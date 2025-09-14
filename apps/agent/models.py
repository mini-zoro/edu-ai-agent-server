import uuid
from django.db import models
from AAServer.common.models import BaseModel
from apps.auth.models import User
# Create your models here.


class Tag(BaseModel):
    """
    标签模型
    """
    id = models.BigIntegerField(primary_key=True, db_comment='标签ID')
    name = models.CharField(max_length=255, db_comment='标签名称')
    description = models.TextField(db_comment='标签描述')
    sequence = models.IntegerField(db_comment='标签排序')

    class Meta:
        db_table = 'tag'
        db_table_comment = '标签表'
        ordering = ['sequence', 'name']

    def __str__(self):
        return self.name


class Agent(BaseModel):
    """
    智能体模型
    """
    AGENT_TYPE_CHOICES = [
        (0, '共同使用'),
        (1, '老师专用'),
        (2, '学生专用'),
    ]
    id = models.BigIntegerField(primary_key=True, db_comment='智能体ID')
    name = models.CharField(max_length=255, db_comment='智能体名称')
    description = models.TextField(db_comment='智能体描述')
    avatar = models.ForeignKey('resource.Resource', on_delete=models.SET_NULL,
                               null=True, blank=True, db_comment='智能体头像资源ID')
    baseurl = models.CharField(
        max_length=255, db_comment='智能体API请求地址', )
    apikey = models.CharField(
        max_length=255, db_comment='智能体api请求的认证key', )
    usage_count = models.IntegerField(db_comment='智能体使用用户数', default=0)
    agent_type = models.IntegerField(
        db_comment='智能体类型', choices=AGENT_TYPE_CHOICES, default=0)
    tags = models.ManyToManyField(
        Tag,
        through='AgentTag',
        related_name='agents',
    )

    class Meta:
        db_table = 'tb_agent'
        db_table_comment = '智能体表'
        ordering = ['-create_time']

    def __str__(self):
        return self.name

    def can_used_by(self, user):
        """
        判断智能体是否可以被用户使用
        """
        if user.type == 0:  # 管理员
            return True
        if self.agent_type == 0:  # 共同专用
            return True
        elif self.agent_type == 1:  # 教师专用
            return user.type == 1
        elif self.agent_type == 2:  # 学生专用
            return user.type == 2


class AgentTag(BaseModel):
    """
    智能体标签关联表
    """
    agent = models.ForeignKey(
        Agent,
        on_delete=models.RESTRICT,
        db_comment='智能体ID'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.RESTRICT,
        db_comment='标签ID'
    )

    class Meta:
        db_table = 'tb_agent_tag'
        db_table_comment = '智能体标签关联表'

    def __str__(self):
        return f"{self.agent.name}-{self.tag.name}"


class Conversation(BaseModel):
    """
    对话模型
    """
    # 使用 UUID 作为主键，方便与 Dify API 的 conversation_id 对应
    id = models.BigIntegerField(primary_key=True, db_comment='消息ID')
    conversation_id = models.UUIDField(default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        Agent, on_delete=models.RESTRICT, db_comment='所属智能体')
    user = models.ForeignKey(
        User, on_delete=models.RESTRICT, db_comment='所属用户')
    title = models.CharField(max_length=255, db_comment='对话标题')

    class Meta:
        db_table = 'conversation'
        db_table_comment = '对话会话表'
        ordering = ['-update_time']

    def _str_(self):
        return f"{self.user.account}-{self.title}"


class Message(BaseModel):
    """
    对话消息模型
    """
    class Role(models.TextChoices):
        USER = 'user', '用户'
        ASSISTANT = 'assistant', '智能体'
    id = models.BigIntegerField(primary_key=True, db_comment='消息ID')
    conversation = models.ForeignKey(
        Conversation, on_delete=models.RESTRICT, related_name="messages", db_comment='所属对话')
    content = models.TextField(db_comment='消息内容')
    role = models.CharField(
        max_length=10, choices=Role.choices, verbose_name="角色")
    related_questions = models.JSONField(
        blank=True, null=True, db_comment='相关推荐问题')
    metadata = models.JSONField(blank=True, null=True, db_comment='消息元数据')
    # 使用 UUID 作为主键，方便与 Dify API 的 message_id 对应
    message_id = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        db_table = 'message'
        db_table_comment = '对话消息表'
        ordering = ['-create_time']

    def _str_(self):
        return f"{self.conversation.title}-{self.role}"
