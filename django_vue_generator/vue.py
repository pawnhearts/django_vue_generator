import json
import types

from django_vue_generator.utils import vuetify


# class VueGenerator:
#     postfix = ""
#
#     def __init__(self, serializer):
#         self.serializer = serializer
#
#     @property
#     def model_name(self):
#         return self.serializer.Meta.model._meta.model_name
#
#     @property
#     def pk_name(self):
#         return self.serializer.Meta.model._meta.pk.name
#
#     @property
#     def component_name(self):
#         return f"{self.model_name.title()}{self.postfix}"
#
#     @property
#     def filename(self):
#         return f"frontend/src/components/{self.component_name}.vue"
#
#     @property
#     def fields(self):
#         return self.serializer().fields.items()
#
#     def _template(self):
#         yield "<template>"
#         yield from filter(None, self.template())
#         yield "</template>"
#
#     def _style(self):
#         yield "<style>"
#         yield from filter(None, self.style())
#         yield "</style>"
#
#     def _script(self):
#         yield """<script>"""
#         yield from filter(None, self.imports())
#         yield "export default {"
#         yield f'name: "{self.component_name}",'
#         yield from self.script()
#         yield ",".join(
#             f"{name} {{{value}}}" for name, value in self._script_items()
#         )
#         yield "};"
#         yield "</script>"
#
#     def _script_items(self):
#         yield "data()", "".join(self._data())
#         yield from filter(None, self.script_items())
#         yield "methods:", ",".join(
#             f"{name} {{{body}}}" for name, body in filter(None, self.methods())
#         )
#         yield "watch:", ",".join(
#             f"{name} {{{body}}}" for name, body in filter(None, self.watch())
#         )
#         yield "computed:", ",".join(
#             f"{name}: () => {{{body}}}"
#             for name, body in filter(None, self.computed())
#         )
#
#     def _data(self):
#         yield """return {"""
#         yield ",".join(f"{name}: {val}" for name, val in filter(None, self.data()))
#         yield "}"
#
#     def data(self):
#         yield
#
#     def script_items(self):
#         yield
#
#     def methods(self):
#         yield
#
#     def watch(self):
#         yield
#
#     def computed(self):
#         yield
#
#     def imports(self):
#         yield
#
#     def template(self):
#         yield
#
#     def style(self):
#         yield
#
#     def render(self):
#         return vuetify(
#             "".join(
#                 "".join(gen()) for gen in [self._template, self._script, self._style]
#             )
#         )


class js_str(str):
    def __new__(cls, *args):
        return super().__new__(cls, cls.call(*args))

    @staticmethod
    def call(v):
        return v


class js_callable(js_str):
    pass


class js_func(js_callable):
    @staticmethod
    def call(args, body):
        args = args if isinstance(args, str) else ",".join(args or [])
        # if 'return' in body: body = f'{{{body}}}'
        # return f"({args}) => {body}"
        return f"({args}) {{{body}}}"


class js_lambda(js_callable):
    @staticmethod
    def call(args, body):
        args = args if isinstance(args, str) else ",".join(args or [])
        if "return" in body:
            body = f"{{{body}}}"
        return f"({args}) => {body}"


class py_to_js(js_str):
    @staticmethod
    def call(d):
        if isinstance(d, dict) or isinstance(d, types.GeneratorType):
            return "{{{}}}".format(
                ",".join(
                    f"{k}{'' if isinstance(v, js_func) else ': '}{v if isinstance(v, js_str) else py_to_js(v)}"
                    for k, v in iter_items(d)
                )
            )
        elif isinstance(d, js_func):
            return d
        else:
            return json.dumps(d)


def iter_items(d):
    if callable(d):
        d = d()
    if isinstance(d, types.GeneratorType):
        return d
    else:
        return d.items()


class Vue:
    """
    data, methods, computed, watch and other properties of the class can be:
        a dict
        a property or method returning dict
        a property or method returning generator of (key, value)
    and it generates js object(except "data" which generates method which returns js object)

    values from those dict are going through json.dumps unless it's instance of:
    js_str(value) - value is used as is
    js_func(args, func_body) - creates function like "foo(arg1) { func_body }"
    js_lambda(args, func_body) - creates function like "foo: => (arg1) { func_body }"
        (if there is no "return" in func_body it would use "foo: => (arg1) func_body")
    if methods, computed or watch value is not js_func or js_lambda it's automatically converted to js_func
        (with no argumens or (newVal, oldVal) arguments in case of watch).
    data, mounted and created automatically converted to js_func too.


    example:
    class Test(Vue):
        data = {'a': [1, 2, 3], 'component_name': js_str('this.name')}
        computed = {'b': js_lambda("", "this.name"), 'c': js_lambda("", "let c=3; return c;"), 'd': 'return 4'}

        @property
        def methods(self):
            yield 'do_a', js_func('a', 'return 1')
            yield 'do_b', 'return 2'

        props = ['p']
        watch = {'p': 'do_a(newVal)'}

    would output:
        data() {
            return {
                a: [1, 2, 3],
                component_name: this.name
            };
        },
        methods: {
            do_a(a) { return 1 },
            do_b() { return 2 }
        },
        props: ["p"],
        watch: {
            p(newVal, oldVal) { do_a(newVal) }
        },
        computed: {
            b: () => this.name,
            c: () => { let c = 3; return c; },
            d() { return 4 }
        }

    template and style methods should return str.
    or template objeect like:
        def template(self):
            import jinja2
            return jinja2.Template('<div><h1>{{name}}</h1><span v-for="i in a" :key="i">{% raw %}{{i}}{% endraw %}</span></div>')
    then render method would be called with self as context
    outputs
        <div>
            <h1>vue</h1>
            <span v-for="i in a" :key="i">{{i}}</span>
        </div>


    docstrings are added as tag attributes. example:
        def style(self):
            ' language="scss" '
            return '.test{border:1;}'
    outputs:
        <style language="scss">
            .test { border: 1; }
        </style>



    """

    @property
    def name(self):
        return self.__class__.__name__.lower()

    data = {}
    computed = {}
    methods = {}
    watch = {}
    props = {}
    mounted = None
    created = None
    imports = ""

    def style(self):
        pass

    def template(self):
        return f"<div>\n<h1>{self.name}</h1>\n</div>"

    def script(self):
        items = [f"name: {repr(self.name)}"]
        for k in [
            "data",
            "methods",
            "computed",
            "props",
            "watch",
            "mounted",
            "created",
            "validations",
        ]:
            v = getattr(self, k, None)
            if v:
                if k == "data":
                    v = js_func("", f"return {py_to_js(v)}")
                if k in ("watch", "methods", "computed"):
                    default_args = ("newVal", "oldVal") if k == "watch" else ()
                    v = {
                        k: v if isinstance(v, js_callable) else js_func(default_args, v)
                        for k, v in iter_items(getattr(self, k))
                    }
                if k in ("mounted", "created"):
                    if not isinstance(v, js_callable):
                        v = js_func((), v)
                items.append(
                    f"""{k}{'' if isinstance(v, js_callable) else ': '}{py_to_js(v)}"""
                )

        return "{}\n\nexport default {{{}}};".format(self.imports, ",".join(items))

    def render(self):
        result = ""
        for tag in ["template", "script", "style"]:
            v = getattr(self, tag, None)
            if callable(v):
                v = v()
            if isinstance(v, types.GeneratorType):
                v = "\n".join(v)
            if hasattr(v, "render"):
                context = {k: getattr(self, k) for k in dir(self)}
                if v.__class__.__module__.startswith("django"):
                    from django.template import Context

                    context = Context(context)
                v = v.render(context)
            if v:
                result += (
                    f"""<{tag} {getattr(self, tag).__doc__ or ""}>\n{v}\n</{tag}>\n"""
                )

        return vuetify(result)
