from django.urls import path

from .views import (
    DocumentDetailView,
    DocumentListCreateView,
    DocumentProcessView,
    DocumentSearchView,
)


urlpatterns = [
    path("", DocumentListCreateView.as_view(), name="document-list-create"),
    path("search/", DocumentSearchView.as_view(), name="document-search"),
    path("<int:pk>/process/", DocumentProcessView.as_view(), name="document-process"),
    path("<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
]
