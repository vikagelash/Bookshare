from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter  # იმპორტი
from book.views import BookViewSet

router = DefaultRouter()
router.register('book', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)