from django.urls import path

from .views import DashboardSummaryView, AiSummaryView

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("ai-summary/", AiSummaryView.as_view(), name="ai-summary"),
]

