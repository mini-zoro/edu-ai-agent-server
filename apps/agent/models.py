from django.db import models
from AAServer.common.models import BaseModel
from apps.auth.models import User
# Create your models here.


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
    avatar = models.CharField(
        max_length=255, db_comment='智能体图标存储地址', null=True, blank=True)
    baseurl = models.CharField(
        max_length=255, db_comment='智能体API请求地址', )
    apikey = models.CharField(
        max_length=255, db_comment='智能体api请求的认证key', )
    usage_count = models.IntegerField(db_comment='智能体使用用户数', default=0)
    agent_type = models.IntegerField(
        db_comment='智能体类型', choices=AGENT_TYPE_CHOICES, default=0)
    tags = models.ManyToManyField(
        'code_dict.Code',
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
        if self.agent_type == 0:  # 学生专用
            return user.type == 0
        elif self.agent_type == 1:  # 老师专用
            return user.type == 1
        else:  # 共同使用
            return True


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
        'code_dict.Code',
        on_delete=models.RESTRICT,
        db_comment='标签ID'
    )

    class Meta:
        db_table = 'tb_agent_tag'
        db_table_comment = '智能体标签关联表'
        unique_together = ('agent', 'tag')  # 防止重复关联


class Conversation(BaseModel):
    """
    对话模型
    """
    agent = models.ForeignKey(
        Agent, on_delete=models.RESTRICT, db_comment='所属智能体')
    user = models.ForeignKey(
        User, on_delete=models.RESTRICT, db_comment='所属用户')
    title = models.CharField(max_length=255, db_comment='对话标题')
    conversation_id = models.CharField(
        max_length=255, unique=True, db_comment='Dify会话ID', null=True, blank=True)

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
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, db_comment='所属对话')
    content = models.TextField(db_comment='消息内容')
    role = models.CharField(
        max_length=255, db_comment='角色：user-用户，assistant-AI助手')
    related_questions = models.JSONField(
        blank=True, null=True, db_comment='相关推荐问题')
    metadata = models.JSONField(blank=True, null=True, db_comment='消息元数据')
    message_id = models.CharField(max_length=255, db_comment='Dify消息ID')

    class Meta:
        db_table = 'message'
        db_table_comment = '对话消息表'
        ordering = ['-create_time']

    def _str_(self):
        return f"{self.conversation.title}-{self.role}"
