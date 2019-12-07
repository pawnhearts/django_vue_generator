from django_vue_generator.utils import vuetify


class VueGenerator:
    postfix = ""

    def __init__(self, serializer):
        self.serializer = serializer

    @property
    def model_name(self):
        return self.serializer.Meta.model._meta.model_name

    @property
    def pk_name(self):
        return self.serializer.Meta.model._meta.pk.name

    @property
    def component_name(self):
        return f"{self.model_name.title()}{self.postfix}"

    @property
    def filename(self):
        return f"frontend/src/components/{self.component_name}.vue"

    @property
    def fields(self):
        return self.serializer().fields.items()

    def _template(self):
        yield "<template>\n"
        yield from filter(None, self.template())
        yield "\n</template>\n"

    def _style(self):
        yield "<style>\n"
        yield from filter(None, self.style())
        yield "\n</style>\n"

    def _script(self):
        yield """<script>"""
        yield from filter(None, self.imports())
        yield "export default {"
        yield f'name: "{self.component_name}",'
        yield from self.script()
        yield ",\n".join(
            f"{name} {{\n{value}\n}}" for name, value in self._script_items()
        )
        yield "};"
        yield "</script>"

    def _script_items(self):
        yield "data()", "\n".join(self._data())
        yield from filter(None, self.script_items())
        yield "methods:", ",".join(
            f"{name} {{\n{body}\n}}\n" for name, body in filter(None, self.methods())
        )
        yield "computed:", ",".join(
            f"{name}: () => {{\n{body}\n}}\n"
            for name, body in filter(None, self.computed())
        )

    def _data(self):
        yield """return {"""
        yield ",".join(f"{name}: {val}" for name, val in filter(None, self.data()))
        yield "}"

    def data(self):
        yield

    def script_items(self):
        yield

    def methods(self):
        yield

    def computed(self):
        yield

    def imports(self):
        yield

    def template(self):
        yield

    def style(self):
        yield

    def render(self):
        return vuetify(
            "\n".join(
                "\n".join(gen()) for gen in [self._template, self._script, self._style]
            )
        )
