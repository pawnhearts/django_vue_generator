from rest_framework import viewsets, pagination

from .models import *
from .serializers import get_serializer_class, BookSerializer, AuthorSerializer
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["state"]
    pagination_class = pagination.PageNumberPagination


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = pagination.LimitOffsetPagination


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = get_serializer_class(Publisher)
