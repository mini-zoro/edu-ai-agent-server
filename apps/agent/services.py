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
    def chat_with_agent(agent, query, dify_conversation_id=None, user_id=None, auto_generate_name=True):
        """
        与智能体对话
        """
        base_url = agent.baseurl.rstrip('/')
        if '/v1' not in base_url:
            url = f"{base_url}/v1/chat-messages"
        else:
            url = f"{base_url}/chat-messages"

        headers = {
            'Authorization': f'Bearer {agent.apikey}',
            'Content-Type': 'application/json'
        }
        data = {
            'inputs': {},
            'query': query,
            'response_mode': 'streaming',
            'user': str(user_id) if user_id else str(uuid.uuid4()),
            'files': []  # 添加files字段，即使为空
        }
        # 处理conversation_id - 如果为None则设为空字符串
        if dify_conversation_id is None:
            data['conversation_id'] = ''
        else:
            data['conversation_id'] = str(dify_conversation_id)

        # 添加auto_generate_name字段（如果API支持）
        if auto_generate_name is not None:
            data['auto_generate_name'] = auto_generate_name

        print(f"DEBUG: Dify API请求")
        print(f"  URL: {url}")
        print(f"  Headers: {headers}")
        print(f"  Data: {json.dumps(data, indent=2)}")
        try:
            response = requests.post(
                url, headers=headers, json=data, stream=True)

            print(f"DEBUG: Dify API响应状态码: {response.status_code}")
            print(f"DEBUG: Dify API响应头: {dict(response.headers)}")
            # 如果状态码不是200，打印响应内容
            if response.status_code != 200:
                try:
                    error_content = response.text
                    print(f"DEBUG: API错误响应内容: {error_content}")
                except:
                    pass
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            raise Exception("Dify API请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise Exception("无法连接到Dify服务，请检查服务地址")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # 尝试获取404错误的具体信息
                try:
                    error_content = e.response.text
                    print(f"DEBUG: 404错误响应内容: {error_content}")
                except:
                    pass
                raise Exception("Dify API路径不存在，请检查API地址配置")
            elif e.response.status_code == 401:
                raise Exception("Dify API认证失败，请检查API密钥")
            elif e.response.status_code == 403:
                raise Exception("Dify API访问被拒绝，请检查权限")
            else:
                # 打印响应内容以便调试
                try:
                    error_content = e.response.text
                    print(f"DEBUG: API错误响应内容: {error_content}")
                except:
                    pass
                raise Exception(f"Dify API请求失败: HTTP {e.response.status_code}")
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
    def create_conversation(agent_id, user_id, title=None, user=None):
        """
        创建对话
        """
        try:
            agent = Agent.objects.get(id=agent_id, is_del=0)
        except Agent.DoesNotExist:
            raise ValueError("智能体不存在或已删除")
        if user and not agent.can_used_by(user):
            raise ValueError("您没有权限使用此智能体")
        conversation = Conversation.objects.create(
            agent=agent,
            user_id=user_id,
            title=title or "新对话",
            conversation_id=None  # 初始为None，等待Dify返回
        )
        return conversation

    @staticmethod
    def update_conversation_id(conversation_id, dify_conversation_id):
        """
        更新对话的Dify conversation_id
        """
        try:
            conversation = Conversation.objects.get(
                id=conversation_id, is_del=0)
            conversation.conversation_id = dify_conversation_id
            conversation.save()
        except Conversation.DoesNotExist:
            raise ValueError("对话不存在或已删除")

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
        user_count = Conversation.objects.filter(
            agent_id=agent_id, is_del=0).values('user_id').distinct().count()
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
    def get_conversation_messages(conversation_id, user_id):
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
                is_del=0)
        except Conversation.DoesNotExist:
            return None

    @staticmethod
    def delete_conversation(conversation_id, user_id):
        """
        删除对话
        """
        try:
            updated_count = Conversation.objects.filter(
                id=conversation_id,
                is_del=0,
                user_id=user_id
            ).update(is_del=1)
            return True
        except Conversation.DoesNotExist:
            return False

    @staticmethod
    def update_conversation_title(conversation_id, user_id, title):
        """
        更新对话标题
        """
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                is_del=0,
                user_id=user_id
            )
            conversation.title = title
            conversation.save()
            return conversation
        except Conversation.DoesNotExist:
            return None
