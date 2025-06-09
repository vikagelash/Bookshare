from rest_framework import generics
from book.models import Book
from .serializers import BookSerializer


class BookList(generics.GenericAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


