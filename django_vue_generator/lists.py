from django.urls import get_resolver
from rest_framework import serializers, pagination
from django_vue_generator.vue import js_func, js_str, Vue


class ListGenerator(Vue):
    postfix = "List"

    def __init__(
        self, viewset, table_tag="table", row_tag="tr", column_tag="td", header_tag="th"
    ):
        self.table_tag = table_tag
        self.row_tag = row_tag
        self.column_tag = column_tag
        self.header_tag = header_tag
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
        self.retrieve_url = retrieve_url and retrieve_url[0][0][0][0].rsplit("/", 2)[0]
        self.viewset = viewset
        serializer = viewset().get_serializer_class()
        self.serializer = serializer
        self.model_name = self.serializer.Meta.model._meta.model_name
        self.pk_name = self.serializer.Meta.model._meta.pk.name
        self.component_name = f"{self.model_name.title()}{self.postfix}"
        self.filename = f"frontend/src/components/{self.component_name}.vue"
        self.fields = self.serializer().fields.items()

    def template(self):
        return "".join(self._template())

    def _template(self):
        yield f'<div class="{self.model_name}_list">'
        yield f"<{self.table_tag}>"
        yield f'<slot name="header" v-bind:object="object">'
        yield f"<{self.row_tag}>"
        for name, field in self.fields:
            yield f"<{self.header_tag}>{field.label}</{self.header_tag}>"
        yield f"</{self.row_tag}>"
        yield f"</slot>"
        yield f'<{self.row_tag} v-for="object in objects" :key="object.{self.pk_name}">'
        yield f'<slot name="object" v-bind:object="object">'
        for name, field in self.fields:
            yield f"<{self.column_tag}>{{{{ object.{name} }}}}</{self.column_tag}>"
        yield f"</slot>"
        yield f"</{self.row_tag}>"
        yield f"</{self.table_tag}>"
        yield from self.pagination()
        yield "</div>"

    def pagination(self):
        if issubclass(self.viewset.pagination_class, pagination.PageNumberPagination):
            yield f'<slot name="pagination" :count="count" :page="page" :page_size="page_size">'
            yield '<select v-model="page">'
            yield f'<option v-for="p in pages()" :key="p">{{{{ p }}}}</option>'
            yield f"</select>"
            yield f"</slot>"
        elif issubclass(
            self.viewset.pagination_class, pagination.LimitOffsetPagination
        ):
            yield f'<slot name="pagination" :count="count" :offset="offset" :limit="limit">'
            yield '<select v-model="offset">'
            yield f'<option v-for="[off, p] in offsets()" :key="p" :value="off">{{{{ p }}}}</option>'
            yield f"</select>"
            yield f"</slot>"
        else:
            yield

    props = ["filters"]

    mounted = js_func("", """this.list(this.filters);""")

    def watch(self):
        yield "filters", js_str(
            """handler (newVal, oldVal) {
        if(this.page) this.page=1;
        if(this.offset) this.offset=0;
        this.list(newVal);
        }, deep: true"""
        )
        yield "page", "this.list(this.filters);"
        yield "offset", "this.list(this.filters);"

    @property
    def data(self):
        yield "objects", []
        yield "count", 0
        if issubclass(self.viewset.pagination_class, pagination.PageNumberPagination):
            yield "page", 1
            yield "page_size", self.viewset.pagination_class.page_size
        elif issubclass(
            self.viewset.pagination_class, pagination.LimitOffsetPagination
        ):
            yield "limit", self.viewset.pagination_class.default_limit
            yield "offset", 0

    def methods(self):
        yield "list", js_func(
            "filters",
            f"""
        let page_params=this.page?{{page:this.page}}:(this.limit?{{offset:this.offset, limit:this.limit}}:{{}});
        this.$http.get('{self.list_url}', {{params:{{...page_params, ...filters}}}}).then(r => r.json()).then(
        r => {{
        if(r.results) {{
            this.objects = r.results;
            this.count = r.count;
        }} else {{
            this.objects = r;
        }}
        }}
        );""",
        )
        yield "pages", """let res=[];
        for(let i=1;i<=Math.ceil(this.count/this.page_size);i++){
        res.push(i);
        }
        return res;"""
        yield "offsets", """let res=[], j=1;
        for(let i=0;i<=this.count;i+=this.limit){
        res.push([i, j]);
        j++;
        }
        return res;"""

    # def get_filters(self):
    #     filters = []
    #     for backend in self.viewset.filter_backends:
    #         back = backend()
    #         if hasattr(back, 'get_filterset'):
    #             fs = back.get_filterset(self.request, self.queryset, self.view)
    #             if fs:
    #                 for n, q in fs.get_filters().items():
    #                     field = q.field_name.replace('__', '.')
    #                     lookup = f'${q.lookup_expr}'.replace('exact', 'eq').replace('contains', 'regex')
    #                     params = {'data_key': repr(field), 'required': q.field.required, 'params': {}}
    #                     if hasattr(q.field, 'choices'):
    #                         choices = (q.field.choices() if callable(q.field.choices) else q.field.choices)
    #                     filters.append({'q': n, 'lookup_field': field, 'params': params})
    #
    #                 if getattr(self.viewset, 'ordering_fields', None):
    #                     filters.append({
    #                         'q': 'ordering',
    #                         'lookup_field': None,
    #                         'validate': {'validate': 'validate.OneOf({})'.format(repr(self.viewset.ordering_fields))},
    #                         'field_type': 'Str',
    #                         'params': {}
    #                     })
    #     return filters
