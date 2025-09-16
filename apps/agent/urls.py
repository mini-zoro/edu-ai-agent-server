from django.urls import path
import apps.agent.views
from apps.rbac.constants import PERMISSION_KEY

urlpatterns = [
     #智能体管理
    path('/agents', apps.agent.views.AgentView.as_view(),
         name='agents'),
    path('/agents/manage', apps.agent.views.AgentManageView.as_view(),
         kwargs={PERMISSION_KEY: 'common:agent:manage'}, name='agent_manage'),
    path('/agents/<int:agent_id>', apps.agent.views.AgentDetailView.as_view(),
         name='agent_detail'),
    #标签管理
    path('/tags', apps.agent.views.TagView.as_view(),
         name='tags'),
    path('/tags/manage', apps.agent.views.TagManageView.as_view(),
         kwargs={PERMISSION_KEY: 'common:agent:tag:manage'}, name='tags_manage'),
    #对话管理
    path('/conversations', apps.agent.views.ConversationView.as_view(),
         name='conversations'),
    #消息管理
    path('/messages', apps.agent.views.MessageView.as_view(),
         name='messages'),
    #聊天接口
    path('/chat', apps.agent.views.ChatView.as_view(),
         name='chat'),
]
