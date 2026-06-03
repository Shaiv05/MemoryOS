from django.urls import path
from .views import GraphDataView, NodeDetailView

urlpatterns = [
    path("data/", GraphDataView.as_view(), name="graph-data"),
    path("nodes/<int:pk>/", NodeDetailView.as_view(), name="node-detail"),
]
