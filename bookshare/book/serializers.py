from rest_framework import serializers
from .models import Book
from user.serializers import UserSerializer


class BookSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Book
        fields = ["title", "author", "genre", "release_year", "slug", "user", "image"]
