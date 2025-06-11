from django.urls import path, include
from rest_framework.routers import DefaultRouter
from book.views import BookViewSet, InterestViewSet

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('interests', InterestViewSet)