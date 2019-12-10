from rest_framework import serializers
from .models import Book, Author, Publisher, Tag


def get_serializer_class(model, fields="__all__", **kwargs):
    return type(
        f"{model.__name__}Serializer",
        (serializers.ModelSerializer,),
        dict(
            **kwargs, **{"Meta": type("Meta", (), {"model": model, "fields": fields})}
        ),
    )


TagSerializer = get_serializer_class(Tag, ["id", "title"], depth=2)
AuthorSerializer = get_serializer_class(
    Author,
    ["id", "name", "email", "books"],
    books=get_serializer_class(Book, ["id", "title"])(many=True),
    depth=2,
)
PublisherSerializer = get_serializer_class(Publisher)
BookSerializer = get_serializer_class(
    Book,
    # ["authors"],
    # authors=get_serializer_class(Author, ["name"])(many=True),
    # tags=TagSerializer(many=True),
    # publisher=PublisherSerializer(),
    depth=2,
)
BookSerializer.Meta.fields = "__all__"
