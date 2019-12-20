import re
from collections import defaultdict

from django.urls import get_resolver
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

from django_vue_generator.utils import vuetify
from django_vue_generator.vue import Vue, js_func, py_to_js, js_str

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


class VueForm(Vue):
    postfix = "Form"

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
        self.serializer = serializer
        self.model_name = self.serializer.Meta.model._meta.model_name
        self.pk_name = self.serializer.Meta.model._meta.pk.name
        self.component_name = f"{self.model_name.title()}{self.postfix}"
        self.filename = f"frontend/src/components/{self.component_name}.vue"
        self.fields = self.serializer().fields.items()

    def template(self):
        return f"""<div class="form pt-6">
        <div class="summary text-red" v-if="$v.form.$error">
          Form has errors
        </div>
        <form @submit.prevent="submit">
          <div class="flex justify-center my-6">
          {''.join(self.form_fields())}
          <div class="text-center">
              <button type="submit" class="button">
                Submit
              </button>
            </div>
            </div>
          </form>
        </div>"""

    def style(self):
        """.hasError{background-color:red;} """

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
                   <strong v-if="errors.{name}">{{{{errors.{name}}}}}</strong>
                  <label class="mr-2 font-bold text-grey">{field.label}</label>"""
            yield f"""<{tag}{input_type} name="{name}" v-model="form.{name}"{'' if hasattr(field, 'iter_options') else '/'}>"""
            if hasattr(field, "iter_options"):
                yield f"""<option :value="k" v-for="(v, k) in options.{name}" :key="k">{{{{v}}}}</option>"""
                yield f"""</{tag.split()[0]}>"""
            if not field.read_only:
                yield """\n</div>"""

    props = ["pk"]

    imports = """import {required, numeric, maxValue, minValue, maxLength, minLength, url, email} from "vuelidate/lib/validators";
            import Vuelidate from 'vuelidate';
            import Vue from 'vue'
            Vue.use(Vuelidate);
            const alwaysInvalid = (value) => false;
            """

    mounted = "if(this.pk){this.fetch(this.pk);}"
    # validations = ", "\n".join(self.validations())

    watch = {"pk": "this.fetch(newVal);"}

    @property
    def data(self):
        options = {}
        fields = {}
        for name, field in self.fields:
            fields[name] = ""
            if hasattr(field, "iter_options"):
                options[name] = {
                    opt.value: opt.display_text for opt in field.iter_options()
                }
        return {
            "serverErrors": False,
            "errors": {},
            "form": fields,
            "options": options,
            "error_messages": self.error_messages(),
        }

    @property
    def validations(self):
        return js_func(
            "",
            """if (this.serverErrors) {
            let serverValidator = {form:{}};
            Object.keys(this.form).forEach(key => {
                serverValidator.form[key] = this.errors[key]?{alwaysInvalid}: {};
            });
            return serverValidator;
            } else {
                return {form: %s};
            }
        """
            % py_to_js(self.validation_items()),
        )

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
                        and f"{k}_{f}: {k}{f.title()}({getattr(field, f'{k}_{f}', None)})"
                        for k in ["min", "max"]
                        for f in ["length", "value"]
                    ],
                ]
                if v
            ]
            yield name, js_str(f'{{{", ".join(validators)}}}')

    def methods(self):
        yield "submit", js_func(
            "",
            """
          this.serverErrors=false;
          this.$v.form.$touch();
          if(this.$v.form.$error){
          Object.keys(this.form).forEach(key => {
            if(!this.$v.form[key].$invalid) return;
            this.errors[key]=this.error_messages[key][(Object.keys(this.error_messages[key]).find(err => {
                return (err!=='invalid' && !this.$v.form[key][err]);
            }) || 'invalid')];
          });
           return;
            }
          if(this.pk) {
            this.update();
          } else {
           this.create();
           }
        """,
        )
        if self.retrieve_url:
            yield "fetch", js_func(
                "pk",
                f"""
            this.$http.get(`{self.retrieve_url}/${{pk}}/`).then(r => r.json()).then(r => {{this.form = r;}});
            """,
            )
            yield "update", js_func(
                "",
                f"""
            this.$http.put(`{self.retrieve_url}/${{this.pk}}/`, {{...this.form}}).then(r => r.json()).then(
            r => {{
                this.serverErrors = false;
                this.form = r;
                this.pk = r.{self.pk_name};
                this.$emit('success', r);
            }},
            err => {{
                this.serverErrors = true;
                this.errors = err.body;
                this.$v.$reset();
                this.$v.$touch();
            }}
            );
            """,
            )
        if self.list_url:
            yield "create", js_func(
                "",
                f""" 
            this.$http.post('{self.list_url}', {{...this.form}}).then(r => r.json()).then(
                r => {{
                    this.serverErrors = false;
                    this.form = r;
                    this.pk = r.{self.pk_name};
                    this.$emit('success', r);
                }},
                err => {{
                    this.serverErrors = true;
                    this.errors = err.body;
                    this.$v.$reset();
                    this.$v.$touch();
                }}
                );
            """,
            )

    def error_messages(self):
        return {
            name: {
                err: msg.format_map(defaultdict(lambda: "", field.__dict__))
                for err, msg in field.error_messages.items()
                if re.match("(required|invalid|(min|max)_(value|length))", err)
                and "None"
                not in msg.format_map(defaultdict(lambda: "", field.__dict__))
                and '""' not in msg.format_map(defaultdict(lambda: "", field.__dict__))
                and not (not field.required and err == "required")
            }
            for name, field in self.fields
        }
