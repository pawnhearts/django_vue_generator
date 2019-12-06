from django.urls import get_resolver
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

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


def _vue_form_generator(viewset):
    if isinstance(viewset, serializers.Serializer):
        serializer = viewset
        list_url = None
        retrieve_url = None
    else:
        list_url = [
            url
            for callback, url in get_resolver().reverse_dict.items()
            if getattr(callback, "cls", None) == viewset
            and "create" in getattr(callback, "actions", {}).values()
        ]
        list_url = list_url and list_url[0][0][0][0]
        retrieve_url = [
            url
            for callback, url in get_resolver().reverse_dict.items()
            if getattr(callback, "cls", None) == viewset
            and "update" in getattr(callback, "actions", {}).values()
        ]
        retrieve_url = retrieve_url and retrieve_url[0][0][0][0].rsplit("/", 2)[0]
        serializer = viewset().get_serializer_class()
    model_name = serializer.Meta.model._meta.model_name
    pk_name = serializer.Meta.model._meta.pk.name
    component_name = f"{model_name.title()}Form"
    yield """<template>
    <div class="form pt-6">
    <div class="summary text-red" v-if="$v.form.$error">
      Form has errors
    </div>
    <form @submit.prevent="submit">
      <div class="flex justify-center my-6">
    """
    for name, field in serializer().fields.items():
        style = default_style[field]
        tag = style["tag"]
        if style.get('input_type', '') == 'file':
            continue
        input_type = ("input_type" in style) and f' type="{style["input_type"]}"' or ""
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

    yield f"""<div class="text-center">
        <button type="submit" class="button">
          Submit
        </button>
      </div>
    </form>
  </div>
  </template>
    <script>
    import {{required, numeric, maxValue, minValue, maxLength, minLength, url, email}} from "vuelidate/lib/validators";
    import Vuelidate from 'vuelidate';
    import Vue from 'vue'
    Vue.use(Vuelidate);

const alwaysInvalid = (value) => false;

export default {{
  name: "{component_name}",

  data() {{
    return {{
    serverErrors: {{}},
    form: {{
    """
    options = {}
    for name, field in serializer().fields.items():
        yield f"""{name}: '',"""
        if hasattr(field, "iter_options"):
            options[name] = {opt.value: opt.display_text for opt in field.iter_options()}
    yield "}, options: {"
    for name, opts in options.items():
        yield f"""{name}: {opts},"""
    yield """
    }
    }
  },
  props: ['pk', 'on_success'],
  watch: {
    pk: (newVal, oldVal) => {if(this.fetch) this.fetch(newVal);}
  },
  validations() {
    if(this.serverErrors) {
        let serverValidator = {form:{}};
        Object.keys(this.form).forEach(key => {
            serverValidator.form[key] = this.serverErrors[key]?{alwaysInvalid}:{};
        });
        return serverValidator;
    } else { return {form: {
    """

    for name, field in serializer().fields.items():
        style = default_style[field]
        validators = [
            v
            for v in [
                field.required and name != pk_name and "required",
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
        yield f"""{name}: {{{', '.join(validators)}}},"""

    yield f"""}}
    }};
    }}
    }},
      methods: {{
    submit() {{
      this.serverErrors={{}};
      this.$v.form.$touch();
      if(this.$v.form.$error) return
      if(this.pk) {{
        this.update();
      }} else {{
       this.create();
       }}
    }},"""
    if retrieve_url:
        yield f"""fetch(pk) {{
        this.$http.get(`{retrieve_url}/${{pk}}/`).then(r => r.json()).then(r => {{this.form = r;}});
        }},
        update() {{
        this.$http.put(`{retrieve_url}/${{this.form.id}}/`, {{...this.form}}).then(r => r.json()).then(
        r => {{
            this.serverErrors = {{}};
            this.form = r;
            this.pk = r.{pk_name};
            if(this.on_success) this.on_success(r.body);
        }},
        err => {{
            this.serverErrors = err.body;
            this.$v.$reset();
            this.$v.$touch();
        }}
        );
        }},"""
    if list_url:
        yield f"""create() {{
        this.$http.post('{list_url}', {{...this.form}}).then(r => r.json()).then(
            r => {{
                this.serverErrors = {{}};
                this.form = r;
                this.pk = r.{pk_name};
                if(this.on_success) this.on_success(r.body);
            }},
            err => {{
                this.serverErrors = err.body;
                this.$v.$reset();
                this.$v.$touch();
            }}
            );
        }},"""
        yield f"""list(filters) {{
        this.$http.get('{list_url}', filters).then(r => r.json()).then(r => {{this.results = r.results;}});
        }},"""
    yield """
  },
  mounted() {
    if(this.pk) {
        this.fetch(this.pk);
    }
  }
    };
    </script>"""

    yield """<style>
    .hasError{background-color:red;} 
    </style>"""
#     yield """<style lang="scss" scoped>
#    @import 'form.scss'
# </style>"""


def generate_vue_form(viewset):
    return "\n".join(_vue_form_generator(viewset))
