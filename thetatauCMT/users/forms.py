from django import forms
from django.conf import settings
from django.utils import timezone
from dal import autocomplete, forward
from address.widgets import AddressWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit
from crispy_forms.bootstrap import FormActions, InlineField, StrictButton, Field
from tempus_dominus.widgets import DatePicker
from allauth.account.forms import LoginForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from core.address import fix_address
from core.models import BIENNIUM_YEARS, forever
from core.forms import DuplicateAddressField, SchoolModelChoiceField
from chapters.models import Chapter, ChapterCurricula
from .models import (
    UserAlter,
    User,
    UserSemesterGPA,
    UserSemesterServiceHours,
    UserOrgParticipate,
    UserStatusChange,
    MemberUpdate,
)


class CaptchaLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.DEBUG:
            captcha = ReCaptchaField(label="", widget=ReCaptchaV3)
            self.fields.update({"captcha": captcha})


class UserListFormHelper(FormHelper):
    form_method = "GET"
    form_id = "user-search-form"
    form_class = "form-inline"
    field_template = "bootstrap3/layout/inline_field.html"
    field_class = "col-xs-3"
    label_class = "col-xs-3"
    form_show_errors = True
    help_text_inline = False
    html5_required = True

    def __init__(self, form=None, rmp_complete=False):
        extra = []
        if rmp_complete:
            extra = [
                Field("rmp_complete"),
            ]
        self.layout = Layout(
            Fieldset(
                '<i class="fas fa-search"></i> Filter Members',
                Row(
                    InlineField("name__icontains"),
                    *extra,
                    InlineField("major"),
                    InlineField("graduation_year__icontains"),
                    FormActions(
                        StrictButton(
                            '<i class="fa fa-search"></i> Filter',
                            type="submit",
                            css_class="btn-primary",
                        ),
                        Submit("cancel", "Clear", css_class="btn-primary"),
                        StrictButton(
                            '<i class="fa fa-download"></i> Download CSV',
                            type="submit",
                            value="Download CSV",
                            name="csv",
                            id="download-csv",
                            css_class="btn-secondary",
                            style="display: none;",
                        ),
                        StrictButton(
                            '<i class="fa fa-envelope-square"></i> Email ALL',
                            type="submit",
                            value="Email ALL",
                            name="email",
                            css_class="btn-danger",
                            id="email-all",
                            style="display: none;",
                        ),
                    ),
                ),
                Row(
                    InlineField("current_status"),
                ),
            ),
        )
        super().__init__(form=form)


class UserRoleListFormHelper(FormHelper):
    form_method = "GET"
    form_id = "user-search-form"
    form_class = "form-inline"
    field_template = "bootstrap3/layout/inline_field.html"
    field_class = "col-xs-3"
    label_class = "col-xs-3"
    form_show_errors = True
    help_text_inline = False
    html5_required = True
    layout = Layout(
        Fieldset(
            '<i class="fas fa-search"></i> Filter Members',
            Row(
                Column(InlineField("name__icontains")),
                Column(InlineField("current_status")),
                Column(InlineField("major")),
                Column(InlineField("graduation_year__icontains")),
                Column(InlineField("region")),
                Column(InlineField("chapter")),
                Column(InlineField("current_roles", style="width:250px")),
                Column(
                    FormActions(
                        StrictButton(
                            '<i class="fa fa-search"></i> Filter',
                            type="submit",
                            css_class="btn-primary",
                        ),
                        Submit("cancel", "Clear", css_class="btn-primary"),
                    )
                ),
            ),
        ),
    )


class AdvisorListFormHelper(FormHelper):
    form_method = "GET"
    form_id = "user-search-form"
    form_class = "form-inline"
    field_template = "bootstrap3/layout/inline_field.html"
    field_class = "col-xs-3"
    label_class = "col-xs-3"
    form_show_errors = True
    help_text_inline = False
    html5_required = True
    layout = Layout(
        Fieldset(
            '<i class="fas fa-search"></i> Filter Advisors',
            Row(
                Column(InlineField("name__icontains")),
                Column(InlineField("region")),
                Column(InlineField("chapter")),
                Column(
                    FormActions(
                        StrictButton(
                            '<i class="fa fa-search"></i> Filter',
                            type="submit",
                            css_class="btn-primary",
                        ),
                        Submit("cancel", "Clear", css_class="btn-primary"),
                    )
                ),
            ),
        ),
    )


class UserLookupForm(forms.Form):
    university = forms.ChoiceField(choices=Chapter.schools())
    badge_number = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.DEBUG:
            captcha = ReCaptchaField(label="", widget=ReCaptchaV3)
            self.fields.update({"captcha": captcha})


class UserUpdateForm(forms.ModelForm):
    badge_number = forms.IntegerField(
        help_text="If you do not know your badge number, leave this blank"
    )
    school_name = SchoolModelChoiceField(
        queryset=Chapter.objects.exclude(active=False).order_by("school"),
        help_text="Where did you attend school while pledging?",
    )
    major = forms.ModelChoiceField(
        queryset=ChapterCurricula.objects.all(),
        help_text="This is the list of currently approved majors, "
        "if your major is not listed please select other and then fill out your major in the box below",
    )
    major_other = forms.CharField(label="Other Major")
    birth_date = forms.DateField(
        label="Birth Date",
        widget=DatePicker(
            options={"format": "M/DD/YYYY"},
            attrs={"autocomplete": "off"},
        ),
    )

    class Meta:
        model = User
        fields = [
            "school_name",
            "badge_number",
            "title",
            "first_name",
            "middle_name",
            "last_name",
            "maiden_name",
            "preferred_pronouns",
            "preferred_name",
            "nickname",
            "suffix",
            "email",
            "email_school",
            "address",
            "birth_date",
            "phone_number",
            "graduation_year",
            "degree",
            "major",
            "major_other",
            "employer",
            "employer_position",
            "employer_address",
            "unsubscribe_paper_gear",
            "unsubscribe_email",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.DEBUG:
            captcha = ReCaptchaField(label="", widget=ReCaptchaV3)
            self.fields.update({"captcha": captcha})
        for key in self.fields:
            self.fields[key].required = False
            if key not in ["degree", "major", "school_name"]:
                self.fields[key].initial = ""


class MemberUpdateForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="users:autocomplete", forward=(forward.Const("false", "chapter"),)
        ),
        required=False,
    )
    outcome = forms.TypedChoiceField(
        choices=(outcome.value for outcome in MemberUpdate.OUTCOME),
        widget=forms.Select(
            attrs={"style": "display: block"},
        ),
    )

    class Meta:
        model = MemberUpdate
        fields = ["outcome", "user"]


class UserDetailChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_name_with_details()


class UserLookupSelectForm(forms.Form):
    users = UserDetailChoiceField(queryset=User.objects.none())

    def __init__(self, *args, **kwargs):
        qs = User.objects.none()
        if "users" in kwargs:
            qs = kwargs.pop("users")
        super().__init__(*args, **kwargs)
        self.fields["users"].queryset = qs
        if not settings.DEBUG:
            captcha = ReCaptchaField(label="", widget=ReCaptchaV3)
            self.fields.update({"captcha": captcha})


class UserLookupSearchForm(forms.ModelForm):
    university = forms.ChoiceField(
        choices=Chapter.schools(),
        help_text="What university did you attend when you pledged Theta Tau",
    )
    id = forms.IntegerField(
        label="Unique ID",
        help_text="This is a unique number sent to you to use "
        "to update your info. If you do not know your unique number, "
        "leave this blank",
    )

    class Meta:
        model = User
        fields = [
            "university",
            "id",
            "name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.DEBUG:
            captcha = ReCaptchaField(label="", widget=ReCaptchaV3)
            self.fields.update({"captcha": captcha})
        for key in self.fields:
            self.fields[key].required = False
            self.fields[key].initial = ""


class UserAlterForm(forms.ModelForm):
    role = forms.ChoiceField(choices=UserAlter.ROLES, required=False)
    chapter = forms.ChoiceField(choices=Chapter.chapter_choices(), required=True)

    class Meta:
        model = UserAlter
        fields = ["chapter", "role"]

    def clean_chapter(self):
        data = self.cleaned_data["chapter"]
        chapter = Chapter.objects.filter(slug=data).first()
        return chapter


class UserForm(forms.ModelForm):
    address = DuplicateAddressField(widget=AddressWidget)

    class Meta:
        model = User
        fields = [
            "preferred_pronouns",
            "preferred_name",
            "major",
            "graduation_year",
            "phone_number",
            "address",
            "email",
        ]

    def __init__(self, *args, **kwargs):
        verify = kwargs.pop("verify", False)
        super().__init__(*args, **kwargs)
        if verify:
            self.fields["major"].widget = forms.HiddenInput()
            self.fields["graduation_year"].widget = forms.HiddenInput()
        else:
            self.fields["email"].widget = forms.HiddenInput()

    def clean_address(self):
        address = self.cleaned_data["address"]
        if address.raw == "None" or address.raw == "":
            raise forms.ValidationError("Address should not be None or blank")
        if not address.locality:
            address = fix_address(address)
        if address is None:
            raise forms.ValidationError("Invalid Address")
        return address


class UserGPAForm(forms.Form):
    user = forms.CharField(
        label="", widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    gpa1 = forms.FloatField(label="", max_value=5.0, min_value=0)  # Fall 2018
    gpa2 = forms.FloatField(label="", max_value=5.0, min_value=0)  # Spring 2019
    gpa3 = forms.FloatField(label="", max_value=5.0, min_value=0)  # Fall 2019
    gpa4 = forms.FloatField(label="", max_value=5.0, min_value=0)  # Spring 2020

    def __init__(self, *args, **kwargs):
        hide_user = kwargs.pop("hide_user", False)
        super().__init__(*args, **kwargs)
        if hide_user:
            self.fields["user"].widget = forms.HiddenInput()

    def save(self):
        user_name = self.cleaned_data["user"]
        user = User.objects.filter(
            name=user_name, chapter__name=self.data["chapter"]
        ).last()
        for i in range(4):
            gpa = self.cleaned_data[f"gpa{i + 1}"]
            if gpa == 0:
                continue
            semester = "sp" if i % 2 else "fa"
            year = BIENNIUM_YEARS[i]
            try:
                obj = UserSemesterGPA.objects.get(
                    user=user,
                    year=year,
                    term=semester,
                )
            except UserSemesterGPA.DoesNotExist:
                obj = UserSemesterGPA(
                    user=user,
                    year=year,
                    term=semester,
                )
            obj.gpa = gpa
            obj.save()


class UserServiceForm(forms.Form):
    user = forms.CharField(
        label="", widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    service1 = forms.FloatField(label="", min_value=0)  # Fall 2018
    service2 = forms.FloatField(label="", min_value=0)  # Spring 2019
    service3 = forms.FloatField(label="", min_value=0)  # Fall 2019
    service4 = forms.FloatField(label="", min_value=0)  # Spring 2020

    def __init__(self, *args, **kwargs):
        hide_user = kwargs.pop("hide_user", False)
        super().__init__(*args, **kwargs)
        if hide_user:
            self.fields["user"].widget = forms.HiddenInput()

    def save(self):
        user_name = self.cleaned_data["user"]
        user = User.objects.filter(
            name=user_name, chapter__name=self.data["chapter"]
        ).last()
        for i in range(4):
            service = self.cleaned_data[f"service{i + 1}"]
            if service == 0:
                continue
            semester = "sp" if i % 2 else "fa"
            year = BIENNIUM_YEARS[i]
            try:
                obj = UserSemesterServiceHours.objects.get(
                    user=user,
                    year=year,
                    term=semester,
                )
            except UserSemesterServiceHours.DoesNotExist:
                obj = UserSemesterServiceHours(
                    user=user,
                    year=year,
                    term=semester,
                )
            obj.service_hours = service
            obj.save()


class UserOrgForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.none())
    start = forms.DateField(
        initial=timezone.now(),
        label="Start Date",
        widget=DatePicker(
            options={"format": "M/DD/YYYY"},
            attrs={"autocomplete": "off"},
        ),
    )
    end = forms.DateField(
        initial=timezone.now() + timezone.timedelta(days=365),
        label="End Date",
        widget=DatePicker(
            options={"format": "M/DD/YYYY"},
            attrs={"autocomplete": "off"},
        ),
    )
    officer = forms.TypedChoiceField(
        coerce=lambda x: x == "True", choices=((False, "No"), (True, "Yes"))
    )

    class Meta:
        model = UserOrgParticipate
        fields = ["user", "org_name", "type", "officer", "start", "end"]

    def __init__(self, *args, **kwargs):
        hide_user = kwargs.pop("hide_user", False)
        super().__init__(*args, **kwargs)
        if hide_user:
            self.fields["user"].widget = forms.HiddenInput()


class ExternalUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "title",
            "phone_number",
            "email",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True


class UserAdminBadgeFixForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    badge_file = forms.FileField(widget=forms.FileInput(attrs={"accept": ".csv"}))


def status_options():
    statuses = []
    for status_option in UserStatusChange.STATUS:
        status, status_display = status_option.value
        if "CC" in status:
            status_display = status_display + " CC"
        statuses.append((status, status_display))
    return statuses


class UserStatusForm(forms.ModelForm):
    status = forms.ChoiceField(label="Status", choices=status_options())

    class Meta:
        fields = ["status", "start", "end"]
        model = UserStatusChange


class UserAdminStatusForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    status = forms.ChoiceField(label="New Status", choices=status_options())
    start = forms.DateField(
        initial=timezone.now(),
        label="Start Date",
        widget=DatePicker(
            options={"format": "M/DD/YYYY"},
            attrs={"autocomplete": "off"},
        ),
    )
    end = forms.DateField(
        initial=forever(),
        label="End Date",
        widget=DatePicker(
            options={"format": "M/DD/YYYY"},
            attrs={"autocomplete": "off"},
        ),
    )
