from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/documents/", include("documents.urls")),
    path("api/graph/", include("graph.urls")),
    path("api/memory/", include("memory.urls")),
    path("api/productivity/", include("productivity.urls")),
    path("api/search/", include("search.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
