from django.urls import path
import apps.agent.views

urlpatterns = [
    path('/agents', apps.agent.views.AgentView.as_view(), name='agents'),
    path('/agents/<int:agent_id>', apps.agent.views.AgentDetailView.as_view(), name='agent_detail'),
]
