import csv
import datetime
from django import forms
from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm
from import_export.admin import ImportExportActionModelAdmin, ImportMixin
from report_builder.admin import Report
from address.admin import Address
from simple_history.admin import SimpleHistoryAdmin
from .forms import (
    UserAdminStatusForm,
    UserAdminBadgeFixForm,
    UserStatusForm,
    status_options,
)
from .models import (
    User,
    UserRoleChange,
    UserStatusChange,
    UserOrgParticipate,
    UserSemesterGPA,
    UserSemesterServiceHours,
    UserAlter,
    ChapterCurricula,
    UserDemographic,
    MemberUpdate,
)
from .resources import UserRoleChangeResource, UserResource, UserStatusChangeResource
from .views import ExportActiveMixin
from forms.models import (
    Depledge,
    Initiation,
    StatusChange,
    CollectionReferral,
    DisciplinaryProcess,
    OSM,
    PrematureAlumnus,
    ResignationProcess,
    ReturnStudent,
    AlumniExclusion,
)
from core.admin import (
    user_chapter,
    ReportAdminSync,
    SentNotificationAdminUpdate,
    SentNotification,
    AddressAdmin,
)
from notes.admin import UserNoteInline, UserNote
from trainings.admin import AssignTrainingMixin, TrainingInline
from core.signals import SignalWatchMixin
from core.models import forever

admin.site.register(Permission)
admin.site.unregister(Report)
admin.site.register(Report, ReportAdminSync)
admin.site.unregister(SentNotification)
admin.site.register(SentNotification, SentNotificationAdminUpdate)
admin.site.unregister(Address)
admin.site.register(Address, AddressAdmin)


def status(obj):
    status = obj.get_status_display()
    if "CC" in obj.status:
        status += " CC"
    return status


class StatusListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Status")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "status"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return status_options()

    def queryset(self, request, queryset):
        return queryset.filter(**self.used_parameters)


class UserStatusChangeAdmin(ImportExportActionModelAdmin):
    raw_id_fields = ["user"]
    list_display = ("user", status, "created", user_chapter, "start", "end")
    list_filter = [StatusListFilter, "created", "user__chapter", "start", "end"]
    ordering = [
        "-created",
    ]
    form = UserStatusForm
    readonly_fields = (
        "created",
        "user",
        "created_by",
        "modified_by",
    )
    search_fields = ["user__name"]
    resource_class = UserStatusChangeResource


admin.site.register(UserStatusChange, UserStatusChangeAdmin)


class UserDemographicAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = (
        user_chapter,
        "gender",
        "sexual",
        "racial",
        "ability",
        "first_gen",
        "english",
    )
    list_filter = [
        "user__chapter",
        "gender",
        "sexual",
        "racial",
        "ability",
        "first_gen",
        "english",
    ]
    search_fields = ["user__chapter__name"]


admin.site.register(UserDemographic, UserDemographicAdmin)


class UserOrgParticipateAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    list_display = ("user", "org_name", "type", "officer", "start", "end")
    list_filter = ["start", "end", "officer", "type"]
    ordering = [
        "-start",
    ]
    readonly_fields = (
        "created_by",
        "modified_by",
    )


admin.site.register(UserOrgParticipate, UserOrgParticipateAdmin)


class UserSemesterGPAAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    list_display = ("user", "gpa", "year", "term")
    list_filter = ["year", "term"]
    ordering = [
        "-year",
    ]
    readonly_fields = (
        "created_by",
        "modified_by",
    )


admin.site.register(UserSemesterGPA, UserSemesterGPAAdmin)


class UserSemesterServiceHoursAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    list_display = ("user", "service_hours", "year", "term")
    list_filter = ["year", "term"]
    ordering = [
        "-year",
    ]
    readonly_fields = (
        "created_by",
        "modified_by",
    )


admin.site.register(UserSemesterServiceHours, UserSemesterServiceHoursAdmin)


class MemberInline(admin.TabularInline):
    model = User
    fields = ["name", "username"]
    readonly_fields = ("name", "username")
    can_delete = False
    ordering = ["name"]
    show_change_link = True

    def has_add_permission(self, _, obj=None):
        return False


class UserRoleChangeAdmin(ImportExportActionModelAdmin):
    list_display = ("user", "role", "start", "end", "created", user_chapter)
    list_filter = ["start", "end", "role", "created", "user__chapter"]
    ordering = [
        "-created",
    ]
    raw_id_fields = ["user"]
    resource_class = UserRoleChangeResource


admin.site.register(UserRoleChange, UserRoleChangeAdmin)


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        # Needs to be duplicated at MyUserAdmin.add_fieldsets
        fields = (
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "chapter",
            "badge_number",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password("")
        if commit:
            user.save()
        return user


class StatusInline(admin.TabularInline):
    model = UserStatusChange
    show_change_link = True
    ordering = ["end"]
    extra = 0
    form = UserStatusForm
    fk_name = "user"


class RoleInline(admin.TabularInline):
    model = UserRoleChange
    fields = ["role", "start", "end"]
    show_change_link = True
    ordering = ["end"]
    extra = 1
    fk_name = "user"


class DepledgeInline(admin.TabularInline):
    model = Depledge
    fields = ["reason", "date", "created"]
    show_change_link = True
    ordering = ["date"]
    extra = 0


class StatusChangeInline(admin.TabularInline):
    model = StatusChange
    fields = ["reason", "date_start", "date_end", "created"]
    show_change_link = True
    ordering = ["date_end"]
    extra = 0
    fk_name = "user"


class InitiationInline(admin.TabularInline):
    model = Initiation
    fields = [
        "date",
        "created",
        "roll",
        "date_graduation",
        "chapter",
        "gpa",
        "test_a",
        "test_b",
    ]
    show_change_link = True
    ordering = ["date"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class CollectionReferralInline(admin.TabularInline):
    model = CollectionReferral
    fk_name = "user"
    readonly_fields = ("created",)
    fields = [
        "balance_due",
        "ledger_sheet",
    ]
    show_change_link = True
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class DisciplinaryProcessInline(admin.TabularInline):
    model = DisciplinaryProcess
    fk_name = "user"
    readonly_fields = ("created",)
    fields = [
        "charges",
        "trial_date",
        "punishment",
        "ec_approval",
    ]
    show_change_link = True
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class AlumniExclusionInline(admin.TabularInline):
    model = AlumniExclusion
    fk_name = "user"
    readonly_fields = ("created", "regional_director")
    fields = [
        "reason",
        "date_start",
        "date_end",
        "voting_result",
        "minutes",
        "regional_director_veto",
        "regional_director",
        "veto_reason",
    ]
    show_change_link = True
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class OSMInline(admin.TabularInline):
    model = OSM
    fk_name = "nominate"
    fields = [
        "meeting_date",
        "year",
        "term",
        "selection_process",
    ]
    show_change_link = True
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class PrematureAlumnusInline(admin.TabularInline):
    model = PrematureAlumnus
    fk_name = "user"
    readonly_fields = ("created",)
    fields = [
        "prealumn_type",
        "approved_exec",
        "exec_comments",
    ]
    show_change_link = True
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class ResignationProcessInline(admin.TabularInline):
    model = ResignationProcess
    fk_name = "user"
    readonly_fields = ("created",)
    fields = [
        "approved_o1",
        "approved_o2",
        "approved_exec",
        "exec_comments",
    ]
    show_change_link = True
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class ReturnStudentInline(admin.TabularInline):
    model = ReturnStudent
    fk_name = "user"
    readonly_fields = ("created",)
    fields = [
        "reason",
        "approved_exec",
        "exec_comments",
    ]
    show_change_link = True
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class UserAlterInline(admin.StackedInline):
    model = UserAlter
    fields = ["chapter", "role"]
    show_change_link = True
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class MyUserAdmin(
    ImportMixin,
    AuthUserAdmin,
    ExportActiveMixin,
    AssignTrainingMixin,
    SignalWatchMixin,
    SimpleHistoryAdmin,
):
    object_type = "user"
    actions = [
        "export_chapter_actives",
        "assign_training",
        "watch_notification_add",
        "watch_notification_remove",
        "update_status",
        "badge_fix",
    ]
    raw_id_fields = ["address"]
    readonly_fields = (
        "deceased_changed",
        "current_roles",
        "current_status",
        "officer",
        "id",
    )
    inlines = [
        UserNoteInline,
        UserAlterInline,
        StatusInline,
        RoleInline,
        InitiationInline,
        StatusChangeInline,
        DepledgeInline,
        PrematureAlumnusInline,
        ReturnStudentInline,
        ResignationProcessInline,
        OSMInline,
        DisciplinaryProcessInline,
        AlumniExclusionInline,
        CollectionReferralInline,
        TrainingInline,
    ]
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    # Needs to be duplicated at MyUserCreationForm.Meta.fields
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "preferred_pronouns",
                    "preferred_name",
                    "email",
                    "chapter",
                    "badge_number",
                ),
            },
        ),
    )
    fieldsets = (
        ("User Profile", {"fields": ("name", "id", "chapter", "badge_number")}),
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "title",
                    "first_name",
                    "middle_name",
                    "last_name",
                    "current_status",
                    "current_roles",
                    "officer",
                    "charter",
                    "no_contact",
                    "address",
                    "deceased",
                    "deceased_date",
                    "deceased_changed",
                    "unsubscribe_paper_gear",
                    "unsubscribe_email",
                    "suffix",
                    "nickname",
                    "preferred_pronouns",
                    "preferred_name",
                    "birth_date",
                    "email",
                    "email_school",
                    "phone_number",
                    "major",
                    "employer",
                    "employer_position",
                    "graduation_year",
                    "class_year",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = (
        "username",
        "id",
        "name",
        "last_login",
        "badge_number",
        "chapter",
        "current_status",
        "current_roles",
        "officer",
    )
    list_filter = (
        "is_superuser",
        "last_login",
        "groups",
        "current_status",
        "officer",
        "chapter",
    )
    search_fields = ("badge_number", "id") + AuthUserAdmin.search_fields
    resource_class = UserResource

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "major":
            try:
                user_pk = request.resolver_match.kwargs.get("object_id")
                if user_pk:
                    user = User.objects.get(id=user_pk)
                    kwargs["queryset"] = ChapterCurricula.objects.filter(
                        chapter=user.chapter
                    )
            except IndexError:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, UserNote):
                user = request.user
                if not change or not hasattr(instance, "created_by"):
                    instance.created_by = user
                instance.modified_by = user
                instance.save()
        formset.save()

    def badge_fix(self, request, queryset):
        if "apply" in request.POST:
            badge_file = request.FILES.get("badge_file")
            decoded_file = badge_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            message = User.fix_badge_numbers(reader)
            self.message_user(request, mark_safe(f"Fix Badge process:<br>{message}"))
            return HttpResponseRedirect(request.get_full_path())
        form = UserAdminBadgeFixForm(
            initial={"_selected_action": queryset.values_list("id", flat=True)}
        )
        return render(
            request,
            "admin/badge_fixes.html",
            context={"form": form},
        )

    badge_fix.short_description = "Fix Badge Numbers"

    def update_status(self, request, queryset):
        if "apply" in request.POST:
            new_status = request.POST.get("status")
            start = request.POST.get("start")
            start = datetime.datetime.strptime(start, "%m/%d/%Y").date()
            end = request.POST.get("end")
            end = datetime.datetime.strptime(end, "%m/%d/%Y").date()
            for user in queryset:
                current_status = user.current_status
                user.set_current_status(new_status, start=start, end=end)
                if end < forever().date():
                    user.set_current_status(current_status, start=end, current=False)
            self.message_user(
                request, f"Set status to {new_status} {start=} {end=} for {queryset}"
            )
            return HttpResponseRedirect(request.get_full_path())
        form = UserAdminStatusForm(
            initial={"_selected_action": queryset.values_list("id", flat=True)}
        )
        return render(
            request,
            "admin/update_status.html",
            context={"form": form},
        )

    update_status.short_description = "Update Status"


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = "action_time"

    list_filter = ["content_type", "action_flag"]

    search_fields = ["object_repr", "change_message"]

    list_display = [
        "action_time",
        "user",
        "content_type",
        "object_link",
        "action_flag",
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse(
                    "admin:%s_%s_change" % (ct.app_label, ct.model),
                    args=[obj.object_id],
                ),
                escape(obj.object_repr),
            )
        return mark_safe(link)

    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"


class MemberUpdateAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    list_display = (
        "user",
        "first_name",
        "last_name",
        "chapter",
        "created",
        "approved",
        "outcome",
    )
    list_filter = [
        "outcome",
        "approved",
        "chapter",
    ]
    ordering = [
        "-created",
    ]
    search_fields = ["user__name", "first_name", "last_name"]


admin.site.register(MemberUpdate, MemberUpdateAdmin)
