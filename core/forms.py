"""
Copied from: https://gist.github.com/jamesbrobb/748c47f46b9bd224b07f
    per: http://stackoverflow.com/questions/15497693/django-can-class-based-views-accept-two-forms-at-a-time/24011448#24011448
"""
import re
from address.models import Locality
from django import forms
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from dal_select2.fields import Select2ListCreateChoiceField
from dal_select2.widgets import Select2Multiple, Select2WidgetMixin, WidgetMixin
from address.forms import AddressField, Address
from core.address import fix_duplicate_address


class SchoolModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.school}"


class MultiFormMixin(ContextMixin):
    form_classes = {}
    prefixes = {}
    success_urls = {}
    grouped_forms = {}

    initial = {}
    prefix = None
    success_url = None

    def get_form_classes(self):
        return self.form_classes

    def get_forms(self, form_classes, form_names=None, bind_all=False):
        return dict(
            [
                (
                    key,
                    self._create_form(
                        key, klass, (form_names and key in form_names) or bind_all
                    ),
                )
                for key, klass in form_classes.items()
            ]
        )

    def _get_form_kwargs(self, form_name, bind_form=False):
        kwargs = {}
        kwargs.update({"initial": self._get_initial(form_name)})
        kwargs.update({"prefix": self._get_prefix(form_name)})
        kwargs_method = "get_%s_kwargs" % form_name
        if hasattr(self, kwargs_method):
            kwargs.update(getattr(self, kwargs_method)())

        if bind_form:
            kwargs.update(self._bind_form_data())

        return kwargs

    def forms_valid(self, forms, form_name):
        form_valid_method = "%s_form_valid" % form_name
        if hasattr(self, form_valid_method):
            return getattr(self, form_valid_method)(forms[form_name])
        else:
            return HttpResponseRedirect(self._get_success_url(form_name))

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))

    def _get_initial(self, form_name):
        initial_method = "get_%s_initial" % form_name
        if hasattr(self, initial_method):
            return getattr(self, initial_method)()
        else:
            return self.initial.copy()

    def _get_prefix(self, form_name):
        return self.prefixes.get(form_name, self.prefix)

    def _get_success_url(self, form_name=None):
        return self.success_urls.get(form_name, self.success_url)

    def _create_form(self, form_name, klass, bind_form):
        form_kwargs = self._get_form_kwargs(form_name, bind_form)
        form_create_method = "create_%s_form" % form_name
        if hasattr(self, form_create_method):
            form = getattr(self, form_create_method)(**form_kwargs)
        else:
            form = klass(**form_kwargs)
        return form

    def _bind_form_data(self):
        if self.request.method in ("POST", "PUT"):
            return {
                "data": self.request.POST,
                "files": self.request.FILES,
            }
        return {}


class ProcessMultipleFormsView(ProcessFormView):
    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        form_name = request.POST.get("action")
        if self._individual_exists(form_name):
            return self._process_individual_form(form_name, form_classes)
        elif self._group_exists(form_name):
            return self._process_grouped_forms(form_name, form_classes)
        else:
            return self._process_all_forms(form_classes)

    def _individual_exists(self, form_name):
        return form_name in self.form_classes

    def _group_exists(self, group_name):
        return group_name in self.grouped_forms

    def _process_individual_form(self, form_name, form_classes):
        forms = self.get_forms(form_classes, (form_name,))
        form = forms.get(form_name)
        if not form:
            return HttpResponseForbidden()
        elif form.is_valid():
            return self.forms_valid(forms, form_name)
        else:
            return self.forms_invalid(forms)

    def _process_grouped_forms(self, group_name, form_classes):
        form_names = self.grouped_forms[group_name]
        forms = self.get_forms(form_classes, form_names)
        if all([forms.get(form_name).is_valid() for form_name in form_classes.keys()]):
            for form_name in form_names:
                response = self.forms_valid(forms, form_name)
            return response
        else:
            return self.forms_invalid(forms)

    def _process_all_forms(self, form_classes):
        forms = self.get_forms(form_classes, None, True)
        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class BaseMultipleFormsView(MultiFormMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """


class MultiFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaying several forms, and rendering a template response.
    """


class DuplicateAddressField(AddressField):
    """
    Django Address does not handle duplicates https://github.com/furious-luke/django-address
    When cleaning if duplicate it just errors
    """

    def to_python(self, value):
        try:
            value = super().to_python(value)
        except Address.MultipleObjectsReturned:
            if (
                not value["street_number"]
                and not value["route"]
                and value["locality"] is None
            ):
                return None
            fix_duplicate_address(value)
            try:
                value = super().to_python(value)
            except Address.MultipleObjectsReturned:
                try:
                    fix_duplicate_address(value)
                except:
                    return None
        return value


class Select2ListCreateMultipleChoiceField(
    Select2ListCreateChoiceField, Select2Multiple
):
    queryset = None

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop("queryset")
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, list):
            return [value]
        new_values = []
        for val in value:
            try:
                val = int(val)
            except ValueError:
                if self.queryset.model == Locality:
                    val = re.search(r"\b\d{5}\b", val).group(0)
                    true_value = self.queryset.filter(postal_code=val).first()
                else:
                    true_value = self.queryset.get(name=val)
                new_values.append(true_value)
            else:
                new_values.append(val)
        return new_values

    def validate(self, value):
        # for create :
        super(forms.ChoiceField, self).validate(value)
        # otherwise you could use :
        # for v in value:
        #     super().validate(v)

    def bound_data(self, data, initial):
        if self.disabled:
            return initial
        return data


class ListSelect2Multiple(WidgetMixin, Select2WidgetMixin, forms.SelectMultiple):
    """Select widget for regular choices and Select2."""


def set_multiple_choices_initial(obj, field_name):
    field = obj.fields[field_name]
    values = getattr(obj.instance, field_name).all()
    if values:
        field.initial = [str(value) for value in values]
        field.choices = [(str(value), str(value)) for value in values.order_by("name")]
