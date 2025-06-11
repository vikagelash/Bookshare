from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from .models import Book, Interest
from .serializers import BookSerializer, InterestSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'author', 'genre', 'release_year']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'accept_interest', 'reject_interest',
                             'interests_list']:
            return [
                permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this book.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to delete this book.")
        instance.delete()


    @action(detail=True, methods=['get'], url_path='interests')
    def interests_list(self, request, pk=None):
        book = self.get_object()
        if book.user != request.user:
            return Response({"detail": "You do not have permission to view interests for this book."},
                            status=status.HTTP_403_FORBIDDEN)

        interests = book.interests.all()
        serializer = InterestSerializer(interests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='accept-interest')
    def accept_interest(self, request, pk=None):
        book = self.get_object()
        if book.user != request.user:
            return Response({"detail": "თქვენ არ გაქვთ ამ წიგნის ინტერესის მიღების ნებართვა."},
                            status=status.HTTP_403_FORBIDDEN)
        if not book.is_available:
            return Response({"detail": "ეს წიგნი უკვე მიუწვდომელია."}, status=status.HTTP_400_BAD_REQUEST)

        interest_id = request.data.get('interest_id')
        if not interest_id:
            return Response({"detail": "ინტერესის ID აუცილებელია."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            interest = book.interests.get(id=interest_id, is_accepted=False, is_rejected=False)
        except Interest.DoesNotExist:
            return Response({"detail": "ინტერესი არ მოიძებნა ან უკვე დამუშავებულია ამ წიგნისთვის."},
                            status=status.HTTP_404_NOT_FOUND)
        interest.is_accepted = True
        interest.save()
        book.is_available = False
        book.save()

        book.interests.filter(is_accepted=False, is_rejected=False).exclude(id=interest_id).update(is_rejected=True)

        return Response({
                            "detail": f"ინტერესის ID {interest_id} მიღებულია. წიგნი '{book.title}' ახლა მიუწვდომელია. სხვა ინტერესები უარყოფილია."},
                        status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='reject-interest')
    def reject_interest(self, request, pk=None):
        book = self.get_object()
        if book.user != request.user:
            return Response({"detail": "თქვენ არ გაქვთ ამ წიგნის ინტერესის უარყოფის ნებართვა."},
                            status=status.HTTP_403_FORBIDDEN)

        interest_id = request.data.get('interest_id')
        if not interest_id:
            return Response({"detail": "ინტერესის ID აუცილებელია."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            interest = book.interests.get(id=interest_id, is_accepted=False, is_rejected=False)
        except Interest.DoesNotExist:
            return Response({"detail": "ინტერესი არ მოიძებნა ან უკვე დამუშავებულია ამ წიგნისთვის."},
                            status=status.HTTP_404_NOT_FOUND)

        interest.is_rejected = True
        interest.save()

        return Response({"detail": f"ინტერესის ID {interest_id} უარყოფილია წიგნისთვის '{book.title}'."},
                        status=status.HTTP_200_OK)


class InterestViewSet(viewsets.ModelViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        book = serializer.validated_data['book']

        if not book.is_available:
            raise serializer.ValidationError({"detail": "This book is not available for request."})
        if book.user == self.request.user:
            raise serializer.ValidationError({"detail": "You cannot express interest in your own book."})
        if Interest.objects.filter(book=book, interested_user=self.request.user).exists():
            raise serializer.ValidationError({"detail": "You have already expressed interest in this book."})


        serializer.save(interested_user=self.request.user)


    def get_queryset(self):
        if self.request.user.is_authenticated:
            my_expressed_interests = Interest.objects.filter(interested_user=self.request.user)
            interests_on_my_books = Interest.objects.filter(book__user=self.request.user)
            return (my_expressed_interests | interests_on_my_books).distinct()

        return Interest.objects.none()

    def perform_update(self, serializer):
        raise serializer.ValidationError({
        "detail": "ინტერესის სტატუსის მართვა შესაძლებელია მხოლოდ წიგნის მფლობელის მიერ სპეციალური მოქმედებების გამოყენებით."})

    def perform_destroy(self, instance):
        if instance.interested_user != self.request.user:
            raise permissions.PermissionDenied("თქვენ არ გაქვთ ამ ინტერესის წაშლის ნებართვა.")
        if instance.is_accepted:
            raise serializer.ValidationError({
                                                  "detail": "მიღებული ინტერესის წაშლა შეუძლებელია. თუ წიგნის მიღება აღარ გსურთ, გთხოვთ, დაუკავშირდით წიგნის მფლობელს."})
        instance.delete()

