import json
import uuid
import requests
from django.conf import settings
from django.db import transaction
from django.db.models import F
from apps.agent.models import Agent, Conversation, Message, AgentTag


class DifyService:
    """
    Dify API服务类
    """
    @staticmethod
    def chat_with_agent(agent, query, conversation_id=None, user_id=None, auto_generate_name=True):
        """
        与智能体对话
        """
        url = f"{agent.baseurl}/chat-messages"
        headers = {
            'Authorization': f'Bearer {agent.apikey}',
            'Content-Type': 'application/json'
        }
        data = {
            'inputs': {},
            'query': query,
            'response_mode': 'streaming',
            'user': str(user_id) if user_id else str(uuid.uuid4()),
            'auto_generate_name': auto_generate_name
        }

        if conversation_id:
            data['conversation_id'] = conversation_id

        try:
            response = requests.post(
                url, headers=headers, json=data, stream=True)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Dify API请求失败: {str(e)}")

    @staticmethod
    def parse_dify_response(response):
        """
        解析Dify API流式响应
        """
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        yield data
                    except json.JSONDecodeError:
                        continue


class ConversationService:
    """
    对话服务类
    """
    @staticmethod
    def create_conversation(agent_id, user_id, title=None,user=None):
        """
        创建对话
        """
        try:
            agent = Agent.objects.get(id=agent_id, is_del=0)
        except Agent.DoesNotExist:
            raise ValueError("智能体不存在或已删除")
        if user and not agent.can_used_by(user):
            raise ValueError("您没有权限使用此智能体")
        conversation_id = str(uuid.uuid4())
        conversation = Conversation.objects.create(
            agent=agent,
            user_id=user_id,
            title=title or "新对话",
            conversation_id=conversation_id
        )
        return conversation

    @staticmethod
    def save_message(conversation, message_id, role, content, related_questions=None, metadata=None):
        """
        保存消息
        """
        message = Message.objects.create(
            conversation=conversation,
            message_id=message_id,
            role=role,
            content=content,
            related_questions=related_questions,
            metadata=metadata
        )
        return message

    @staticmethod
    def update_agent_usage(agent_id):
        """
        更新智能体使用人数
        """
        user_count = Conversation.objects.filter(agent_id=agent_id,is_del=0).values('user_id').distinct().count()
        Agent.objects.filter(id=agent_id).update(
            usage_count=user_count)
        return user_count

    @staticmethod
    def generate_related_questions(content):
        """
        生成相关推荐问题
        """
        # 这里可以调用AI接口生成相关问题，暂时返回示例问题
        return [
            "请详细解释一下这个概念",
            "有什么实际应用场景吗？",
            "与其他相关概念有什么区别？"
        ]

    @staticmethod
    def get_conversation_messgaes(conversation_id,user_id):
        """
        获取对话消息
        """
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                is_del=0,
                user_id=user_id
            )
            return conversation.messages.filter(
                is_del=0,user_id=user_id)
        except Conversation.DoesNotExist:
            return None

    @staticmethod
    def delete_conversation(converstaion_id,user_id):
        """
        删除对话
        """
        try:
            conversation =Conversation.objects.get(
                id=converstaion_id,
                is_del=0,
                user_id=user_id
            )
            conversation.update(is_del=1)
            return True
        except Conversation.DoesNotExist:
            return False

    @staticmethod
    def update_conversation_title(conversation_id,user_id,title):
        """
        更新对话标题
        """
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                is_del=0,
                user_id=user_id
            )
            conversation.update(title=title)
            return conversation
        except Conversation.DoesNotExist:
            return None
