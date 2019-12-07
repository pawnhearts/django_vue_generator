from django.urls import get_resolver
from rest_framework import serializers

from django_vue_generator.vue import VueGenerator


class ListGenerator(VueGenerator):
    postfix = "List"
    table_tag = "table"
    row_tag = "tr"
    column_tag = "td"
    header_tag = "th"

    def __init__(self, viewset):
        if isinstance(viewset, serializers.Serializer):
            serializer = viewset
            self.list_url = None
            self.retrieve_url = None
        else:
            list_url = [
                url
                for callback, url in get_resolver().reverse_dict.items()
                if getattr(callback, "cls", None) == viewset
                and "create" in getattr(callback, "actions", {}).values()
            ]
            self.list_url = list_url and list_url[0][0][0][0]
            retrieve_url = [
                url
                for callback, url in get_resolver().reverse_dict.items()
                if getattr(callback, "cls", None) == viewset
                and "update" in getattr(callback, "actions", {}).values()
            ]
            self.retrieve_url = (
                retrieve_url and retrieve_url[0][0][0][0].rsplit("/", 2)[0]
            )
            serializer = viewset().get_serializer_class()
        super().__init__(serializer)

    def template(self):
        yield f'<div class="{self.model_name}_list">'
        yield f"<{self.table_tag}>"
        yield f"<{self.row_tag}>"
        for name, field in self.fields:
            yield f"<{self.header_tag}>{field.label}</{self.header_tag}>"
        yield f"</{self.row_tag}>"
        yield f'<{self.row_tag} v-for="object in objects" :key="object.{self.pk_name}">'
        yield f'<slot name="object" v-bind:object="object">'
        for name, field in self.fields:
            yield f"<{self.column_tag}>{{{{ object.{name} }}}}</{self.column_tag}>"
        yield f"</slot>"
        yield f"</{self.row_tag}>"
        # pagination slot
        yield f"</{self.table_tag}>"
        yield "</div>"

    def script(self):
        yield "props: ['filters', 'page'],"

    def script_items(self):
        yield "mounted()", """this.list(this.filters);"""
        yield "watch:", """filters: (newVal, oldVal) => {this.list(newVal);}"""

    def data(self):
        yield "objects", "[]"

    def methods(self):
        yield "list(filters)", f"""this.$http.get('{self.list_url}', {{page: this.page || 1, ...filters}}).then(r => r.json()).then(
        r => {{this.objects = r.results?r.results:r;}}
        );"""
