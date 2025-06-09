from django.urls import path
from book.views import BookList, BookDetail

urlpatterns = [
    path("", BookList.as_view(), name="books"),
    path("<int:pk>/", BookDetail.as_view(), name="book detail"),
]
