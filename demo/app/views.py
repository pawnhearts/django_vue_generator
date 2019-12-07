from rest_framework import viewsets
from .models import *
from .serializers import get_serializer_class
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = get_serializer_class(Book)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["state"]


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = get_serializer_class(Author)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["book_set"]


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = get_serializer_class(Publisher)
