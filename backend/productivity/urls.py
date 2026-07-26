from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, TaskViewSet, GoalViewSet

router = DefaultRouter()
router.register(r"notes", NoteViewSet, basename="note")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"goals", GoalViewSet, basename="goal")

urlpatterns = [
    path("", include(router.urls)),
]
