from django.urls import get_resolver
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

from django_vue_generator.utils import vuetify

default_style = ClassLookupDict(
    {
        serializers.Field: {"tag": "input", "input_type": "text"},
        serializers.EmailField: {"tag": "input", "input_type": "email"},
        serializers.URLField: {"tag": "input", "input_type": "url"},
        serializers.IntegerField: {"tag": "input", "input_type": "number"},
        serializers.FloatField: {"tag": "input", "input_type": "number"},
        serializers.DateTimeField: {"tag": "input", "input_type": "datetime-local"},
        serializers.DateField: {"tag": "input", "input_type": "date"},
        serializers.TimeField: {"tag": "input", "input_type": "time"},
        serializers.FileField: {"tag": "input", "input_type": "file"},
        serializers.BooleanField: {"tag": "checkbox"},
        serializers.ChoiceField: {"tag": "select",},  # Also valid: 'radio'
        serializers.MultipleChoiceField: {
            "tag": "select_multiple",  # Also valid: 'checkbox_multiple'
        },
        serializers.RelatedField: {"tag": "select",},  # Also valid: 'radio'
        serializers.ManyRelatedField: {
            "tag": "select multiple",  # Also valid: 'checkbox_multiple'
        },
        serializers.Serializer: {"tag": "fieldset"},
        serializers.ListSerializer: {"tag": "list_fieldset"},
        serializers.ListField: {"tag": "list_field"},
        serializers.DictField: {"tag": "dict_field"},
        serializers.FilePathField: {"tag": "input", "input_type": "file"},
        serializers.JSONField: {"tag": "textarea",},
    }
)


class FormGenerator:
    def __init__(self, viewset):
        if isinstance(viewset, serializers.Serializer):
            self.serializer = viewset
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
            self.serializer = viewset().get_serializer_class()

    @property
    def model_name(self):
        return self.serializer.Meta.model._meta.model_name

    @property
    def pk_name(self):
        return self.serializer.Meta.model._meta.pk.name

    @property
    def component_name(self):
        return f"{self.model_name.title()}Form"

    @property
    def filename(self):
        return f"frontend/src/components/{self.component_name}.vue"

    @property
    def fields(self):
        return self.serializer().fields.items()

    def template(self):
        yield "<template>\n"
        yield """<div class="form pt-6">
        <div class="summary text-red" v-if="$v.form.$error">
          Form has errors
        </div>
        <form @submit.prevent="submit">
          <div class="flex justify-center my-6">
        """
        yield from self.form_fields()
        yield f"""<div class="text-center">
              <button type="submit" class="button">
                Submit
              </button>
            </div>
          </form>
        </div>"""
        yield "\n</template>\n"

    def style(self):
        yield """
        <style>
        .hasError{background-color:red;} 
        </style>"""

    def form_fields(self):
        for name, field in self.fields:
            style = default_style[field]
            tag = style["tag"]
            if style.get("input_type", "") == "file":
                continue
            input_type = (
                ("input_type" in style) and f' type="{style["input_type"]}"' or ""
            )
            if field.read_only:
                tag = "input"
                input_type = ' type="hidden"'
            else:
                yield f"""<div
                   :class="{{ 'hasError': $v.form.{name}.$error }}">
                   <strong v-if="serverErrors.{name}">{{{{serverErrors.{name}}}}}</strong>
                  <label class="mr-2 font-bold text-grey">{field.label}</label>"""
            yield f"""<{tag}{input_type} name="{name}" v-model="form.{name}"{'' if hasattr(field, 'iter_options') else '/'}>"""
            if hasattr(field, "iter_options"):
                yield f"""<option :value="k" v-for="(v, k) in options.{name}" :key="k">{{{{v}}}}</option>"""
                yield f"""</{tag.split()[0]}>"""
            if not field.read_only:
                yield """\n</div>"""

    def script(self):
        yield """<script>"""
        yield """import {required, numeric, maxValue, minValue, maxLength, minLength, url, email} from "vuelidate/lib/validators";
            import Vuelidate from 'vuelidate';
            import Vue from 'vue'
            Vue.use(Vuelidate);
            const alwaysInvalid = (value) => false;
            """
        yield "export default {"
        yield f'name: "{self.component_name}",'
        yield "props: ['pk'],"
        yield ",\n".join(
            f"{name} {{\n{value}\n}}" for name, value in self.script_items()
        )
        yield """};\n</script>"""

    def script_items(self):
        yield "data()", "\n".join(self.data())
        if self.retrieve_url:
            yield "watch:", """pk: (newVal, oldVal) => {this.fetch(newVal);}"""
            yield "mounted()", """if(this.pk){this.fetch(this.pk);}"""
        yield "validations()", "\n".join(self.validations())
        yield "methods:", ",".join(
            f"{name} {{\n{body}\n}}" for name, body in self.methods()
        )

    def data(self):
        yield """return {
                serverErrors: {},
                form: {
                    """
        options = {}
        for name, field in self.fields:
            yield f"""{name}: '', """
            if hasattr(field, "iter_options"):
                options[name] = {
                    opt.value: opt.display_text for opt in field.iter_options()
                }
        yield "}, options: {"
        for name, opts in options.items():
            yield f"""{name}: {opts}, """
        yield "}"
        yield "}"

    def validations(self):
        yield """if (this.serverErrors) {
            let serverValidator = {form:{}};
            Object.keys(this.form).forEach(key => {
                serverValidator.form[key] = this.serverErrors[key]?{alwaysInvalid}: {};
            });
            return serverValidator;
            } else {
            return {form: {
            """
        yield ",\n".join(
            f'"{name}": {{{validators}}}'
            for name, validators in self.validation_items()
        )
        yield """}};}"""

    def validation_items(self):
        for name, field in self.fields:
            style = default_style[field]
            validators = [
                v
                for v in [
                    field.required and name != self.pk_name and "required",
                    style.get("input_type", None) in ("number", "url", "email")
                    and f"{style['input_type'].replace('number', 'numeric')}",
                    *[
                        getattr(field, f"{k}_{f}", None)
                        and f"{k}: {k}{f.title()}({getattr(field, f'{k}_{f}', None)})"
                        for k in ["min", "max"]
                        for f in ["length", "value"]
                    ],
                ]
                if v
            ]
            yield name, ", ".join(validators)

    def methods(self):
        yield "submit()", """
          this.serverErrors={};
          this.$v.form.$touch();
          if(this.$v.form.$error) return
          if(this.pk) {
            this.update();
          } else {
           this.create();
           }
        """
        if self.retrieve_url:
            yield "fetch(pk)", f"""
            this.$http.get(`{self.retrieve_url}/${{pk}}/`).then(r => r.json()).then(r => {{this.form = r;}});
            """
            yield "update()", f"""
            this.$http.put(`{self.retrieve_url}/${{this.pk}}/`, {{...this.form}}).then(r => r.json()).then(
            r => {{
                this.serverErrors = {{}};
                this.form = r;
                this.pk = r.{self.pk_name};
                this.$emit('success', r);
            }},
            err => {{
                this.serverErrors = err.body;
                this.$v.$reset();
                this.$v.$touch();
            }}
            );
            """
        if self.list_url:
            yield "create()", f""" 
            this.$http.post('{self.list_url}', {{...this.form}}).then(r => r.json()).then(
                r => {{
                    this.serverErrors = {{}};
                    this.form = r;
                    this.pk = r.{self.pk_name};
                    this.$emit('success', r);
                }},
                err => {{
                    this.serverErrors = err.body;
                    this.$v.$reset();
                    this.$v.$touch();
                }}
                );
            """
            yield "list(filters)", f"""this.$http.get('{self.list_url}', filters).then(r => r.json()).then(
            r => {{this.results = r.results;}}
            );"""

    def render(self):
        return vuetify(
            "\n".join(
                "\n".join(gen()) for gen in [self.template, self.script, self.style]
            )
        )
