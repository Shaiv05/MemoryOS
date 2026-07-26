from django.urls import path

from .views import MemoryEntryDetailView, MemoryEntryListCreateView


urlpatterns = [
    path("", MemoryEntryListCreateView.as_view(), name="memory-entry-list-create"),
    path("<int:pk>/", MemoryEntryDetailView.as_view(), name="memory-entry-detail"),
]
