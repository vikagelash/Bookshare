from rest_framework import serializers
from .models import Book, Interest
from user.serializers import UserSerializer


class InterestSerializer(serializers.ModelSerializer):
    book_slug = serializers.SlugField(write_only=True, help_text="Slug of the book to express interest in.")
    interested_user_details = UserSerializer(source='interested_user', read_only=True)
    book_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Interest
        fields = [
            'id',
            'book_slug',
            'interested_user_details',
            'book_details',
            'request_date',
            'is_accepted',
            'is_rejected'
        ]

        read_only_fields = [
            'interested_user_details',
            'book_details',
            'request_date',
            'is_accepted',
            'is_rejected'
        ]

    def get_book_details(self, obj):
        return {
            'id': obj.book.id,
            'title': obj.book.title,
            'author': obj.book.author,
            'genre': obj.book.genre,
            'slug': obj.book.slug,
            'is_available': obj.book.is_available,
            'location': obj.book.location,
        }

    def create(self, validated_data):
        book_slug = validated_data.pop('book_slug')
        try:
            book = Book.objects.get(slug=book_slug)
        except Book.DoesNotExist:
            raise serializers.ValidationError({"book_slug": "Book with this slug does not exist."})

        validated_data['book'] = book
        validated_data['interested_user'] = self.context['request'].user

        return super().create(validated_data)


class BookSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    interests = InterestSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "genre",
            "release_year",
            "slug",
            "user",
            "image",
            "is_available",
            "location",
            "interests"
        ]

    read_only_fields = ["slug", "user", "is_available", "interests"]
