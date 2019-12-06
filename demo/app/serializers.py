from rest_framework import serializers
from .models import Book, Author, Publisher


def get_serializer_class(model, fields="__all__", **kwargs):
    return type(
        f"{model.__name__}Serializer",
        (serializers.ModelSerializer,),
        dict(**kwargs, **{"Meta": type("Meta", (), {"model": model, "fields": fields})}),
    )

AuthorSerializer = get_serializer_class(Author, ['id', 'name', 'email'], depth=2)
AuthorSerializer.Meta.fields = ['id', 'name', 'email']
PublisherSerializer = get_serializer_class(Publisher)
BookSerializer = get_serializer_class(Book, ['authors'], authors=AuthorSerializer(Author.objects.all(), many=True), publisher=PublisherSerializer(), depth=2)
BookSerializer.Meta.fields = ['id', 'title', 'authors', 'publisher']
