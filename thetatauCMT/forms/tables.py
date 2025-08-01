from django.utils.safestring import mark_safe
import django_tables2 as tables
from django_tables2.utils import A
from .models import (
    Badge,
    Bylaws,
    Depledge,
    StatusChange,
    Audit,
    PledgeProgram,
    Convention,
    HSEducation,
    OSM,
    CollectionReferral,
    PledgeProgramProcess,
    AlumniExclusion,
)


class BadgeTable(tables.Table):
    class Meta:
        model = Badge
        fields = (
            "name",
            "cost",
            "description",
        )
        attrs = {"class": "table table-striped table-bordered"}


class PledgeFormTable(tables.Table):
    first_pledge = tables.DateColumn(verbose_name="First Pledge Date")
    last_pledge = tables.DateColumn(verbose_name="Last Pledge Date")
    status = tables.Column()
    pledge_names = tables.Column()

    class Meta:
        attrs = {"class": "table table-striped table-bordered"}


class InitiationTable(tables.Table):
    initiation = tables.DateColumn(verbose_name="Initiation Date")
    submitted = tables.DateColumn()
    status = tables.Column()
    member_names = tables.Column()

    class Meta:
        attrs = {
            "class": "table table-striped table-bordered",
        }


class DepledgeTable(tables.Table):
    user = tables.Column(accessor="user__name")
    date = tables.DateColumn(verbose_name="Depledge Date")
    created = tables.DateColumn(verbose_name="Submitted")

    class Meta:
        model = Depledge
        fields = ("user", "date", "created")
        attrs = {"class": "table table-striped table-bordered"}


class StatusChangeTable(tables.Table):
    user = tables.Column(accessor="user__name")
    date_start = tables.DateColumn(verbose_name="Change Date")
    created = tables.DateColumn(verbose_name="Form Submitted")

    class Meta:
        model = StatusChange
        fields = ("user", "date_start", "created", "reason", "date_end")
        attrs = {"class": "table table-striped table-bordered"}


class AuditTable(tables.Table):
    debit_card_access = tables.Column("Debit Card Access")

    class Meta:
        model = Audit
        attrs = {"class": "table table-striped table-bordered"}
        order_by = "-modified"
        fields = [
            "user__chapter",
            "user__chapter__region",
            "modified",
            "dues_member",
            "dues_pledge",
            "frequency",
            "balance_checking",
            "balance_savings",
            "debit_card",
            "debit_card_access",
            "payment_plan",
            "cash_book",
            "cash_book_reviewed",
            "cash_register",
            "cash_register_reviewed",
            "member_account",
            "member_account_reviewed",
        ]


class PledgeProgramTable(tables.Table):
    date_start = tables.DateColumn(verbose_name="Start Date")
    date_complete = tables.DateColumn(verbose_name="Complete Date")
    date_initiation = tables.DateColumn(verbose_name="Initiation Date")
    dues = tables.Column(verbose_name="PNM Dues")
    weeks = tables.Column(verbose_name="Weeks in Program")
    weeks_left = tables.Column(verbose_name="Weeks LEFT in Program")
    live_link = tables.Column(verbose_name="Live Program")
    approval = tables.Column()
    chapter_name = tables.Column(verbose_name="Chapter")
    pk = tables.LinkColumn(
        "forms:pledge_program_detail", verbose_name="Link", args=[A("pk")]
    )

    class Meta:
        model = PledgeProgram
        order_by = "chapter"
        attrs = {"class": "table table-striped table-bordered"}
        fields = [
            "chapter_name",
            "region",
            "school",
            "year",
            "term",
            "live_link",
            "pk",
            "manual",
            "approval",
            "date_start",
            "date_complete",
            "date_initiation",
            "dues",
            "weeks",
            "weeks_left",
        ]

    def render_status(self, value):
        return PledgeProgram.STATUS.get_value(value)

    def render_live_link(self, value):
        if value != "none":
            value = mark_safe(
                f"<a href='https://docs.google.com/document/d/{value}/edit' target='_blank'>Link</a>"
            )
        else:
            value = None
        return value

    def render_term(self, value):
        return PledgeProgram.TERMS.get_value(value)

    def render_manual(self, value):
        return PledgeProgram.MANUALS.get_value(value)

    def render_approval(self, value):
        if value == "not_submitted":
            return "Not Submitted"
        else:
            return PledgeProgramProcess.APPROVAL.get_value(value)


def render_education_category(value, column, record, bound_column):
    column.attrs = {"td": {}}
    if value:
        value = "<br>".join(
            [
                f"{approval}: {bound_column.link(column.render(record, program), value=program, record=record)}"
                for approval, program in value
            ]
        )
        if "Approved" in value:
            column.attrs = {"td": {"bgcolor": "#40B0A6"}}
        elif (
            "Revisions" in value or "Denied" in value
        ) and "Not Reviewed" not in value:
            column.attrs = {"td": {"bgcolor": "#E1BE6A"}}
    else:
        value = ""
    return mark_safe(value)


class HSEducationListTable(tables.Table):
    region = tables.Column()
    alcohol_drugs = tables.FileColumn(verbose_name="Alcohol and Drug Awareness")
    harassment = tables.FileColumn(verbose_name="Anti-Harassment")
    mental = tables.FileColumn(verbose_name="Mental Health Recognition")

    class Meta:
        model = HSEducation
        order_by = "chapter_name"
        attrs = {"class": "table table-striped table-bordered"}
        fields = [
            "chapter__name",
            "region",
            "alcohol_drugs",
            "harassment",
            "mental",
        ]

    def render_alcohol_drugs(self, value, column, record, bound_column):
        return render_education_category(value, column, record, bound_column)

    def render_harassment(self, value, column, record, bound_column):
        return render_education_category(value, column, record, bound_column)

    def render_mental(self, value, column, record, bound_column):
        return render_education_category(value, column, record, bound_column)


class HSEducationTable(tables.Table):
    category = tables.Column()
    approval_comments = tables.Column(verbose_name="Review Comments")
    program_date = tables.DateColumn()

    class Meta:
        model = HSEducation
        order_by = "-program_date"
        attrs = {"class": "table table-striped table-bordered"}
        fields = [
            "program_date",
            "category",
            "approval",
            "approval_comments",
            "report",
        ]

    # def render_approval(self, value):
    #     return HSEducation.APPROVAL.get_value(value)


class RiskFormTable(tables.Table):
    chapter = tables.Column(
        attrs={"td": {"align": "left", "style": "font-weight:bold"}}
    )
    region = tables.Column()
    complete = tables.Column()
    incomplete = tables.Column()

    class Meta:
        attrs = {
            "class": "table table-striped table-bordered",
        }
        # orderable = False


class PrematureAlumnusStatusTable(tables.Table):
    user = tables.Column()
    status = tables.Column()
    approved = tables.Column()
    created = tables.DateColumn()

    class Meta:
        attrs = {
            "class": "table table-striped table-bordered",
        }


class ReturnStudentStatusTable(tables.Table):
    user = tables.Column()
    status = tables.Column()
    approved = tables.Column()
    created = tables.DateColumn()

    class Meta:
        attrs = {
            "class": "table table-striped table-bordered",
        }


class DisciplinaryStatusTable(tables.Table):
    user = tables.Column(verbose_name="Name of Accused")
    status = tables.Column()
    approved = tables.Column()
    created = tables.DateColumn()
    trial_date = tables.DateColumn()
    link = tables.TemplateColumn(
        '{% if record.link %}<a href="{{ record.link }}">Form 2 Link</a>{% endif %}'
    )

    class Meta:
        attrs = {
            "class": "table table-striped table-bordered",
        }


class PledgeProgramStatusTable(tables.Table):
    status = tables.Column()
    approved = tables.Column()
    created = tables.DateColumn()
    term = tables.LinkColumn("forms:pledge_program_detail", args=[A("pk")])

    class Meta:
        attrs = {
            "class": "table table-striped table-bordered",
        }

    def render_term(self, value):
        if value:
            term, year = value.split(" ")
            return f"{PledgeProgram.TERMS.get_value(term)} {year}"
        return value


class SignTable(tables.Table):
    member = tables.Column(order_by=("user"))
    owner = tables.Column(verbose_name="Task Owner")
    role = tables.Column()
    status = tables.Column()
    approved = tables.Column()
    link = tables.TemplateColumn(
        '{% if record.link %}<a href="{{ record.link }}">Sign Link</a>{% endif %}',
        orderable=False,
    )

    class Meta:
        attrs = {
            "class": "table table-striped table-bordered",
        }

    def __init__(self, extra=False, *args, **kwargs):
        extra_columns = kwargs.get("extra_columns", [])
        if extra:
            extra_columns.extend(
                [
                    ("process_name", tables.Column()),
                ]
            )
            kwargs["sequence"] = [
                "process_name",
                "member",
                "owner",
                "role",
                "link",
            ]
            kwargs["exclude"] = ["approved"]
        kwargs["extra_columns"] = extra_columns
        super().__init__(*args, **kwargs)


class ConventionListTable(tables.Table):
    class Meta:
        model = Convention
        order_by = "chapter"
        attrs = {"class": "table table-striped table-bordered"}
        fields = [
            "chapter",
            "region",
            "year",
            "term",
            "delegate",
            "alternate",
        ]


class OSMListTable(tables.Table):
    class Meta:
        model = OSM
        order_by = "chapter"
        attrs = {"class": "table table-striped table-bordered"}
        fields = [
            "chapter",
            "region",
            "year",
            "term",
            "nominate",
        ]


class CollectionReferralTable(tables.Table):
    user = tables.Column(verbose_name="Indebted Member", accessor="user__name")
    created = tables.DateColumn(verbose_name="Submitted")

    class Meta:
        model = CollectionReferral
        fields = ("user", "created")
        attrs = {"class": "table table-striped table-bordered"}


class AlumniExclusionTable(tables.Table):
    user = tables.Column(verbose_name="Excluded Alumni", accessor="user__name")
    regional_director_veto = tables.Column(verbose_name="Regional Director Review")
    veto_reason = tables.Column(verbose_name="RD Reasoning")

    class Meta:
        model = AlumniExclusion
        fields = (
            "user",
            "date_start",
            "date_end",
            "regional_director_veto",
            "veto_reason",
        )
        attrs = {"class": "table table-striped table-bordered"}

    def __init__(self, *args, **kwargs):
        extra_columns = []
        natoff = kwargs.get("natoff", False)
        if natoff:
            self.base_columns["user"] = tables.LinkColumn(
                "viewflow:forms:alumniexclusion:review",
                kwargs={"process_pk": A("pk"), "task_pk": A("task_pk")},
            )
            extra_columns = [
                ("chapter", tables.Column("Chapter")),
                ("chapter.region", tables.Column("Region")),
                ("regional_director", tables.Column("RD Reviewer")),
            ]
            del kwargs["natoff"]
        else:
            self.base_columns["user"] = tables.Column(
                verbose_name="Excluded Alumni", accessor="user__name"
            )
        kwargs["extra_columns"] = extra_columns
        super().__init__(*args, **kwargs)

    def render_regional_director_veto(self, value):
        return value


class ResignationStatusTable(tables.Table):
    description = tables.Column()
    owner = tables.Column()
    started = tables.Column()
    finished = tables.Column()
    status = tables.Column()

    class Meta:
        attrs = {
            "class": "table table-striped table-bordered",
        }


class BylawsListTable(tables.Table):
    class Meta:
        model = Bylaws
        order_by = "-created"
        sequence = (
            "...",
            "created",
            "bylaws",
            "changes",
        )
        fields = (
            "created",
            "bylaws",
            "changes",
        )
        attrs = {"class": "table table-striped table-bordered"}

    def __init__(
        self,
        chapter=False,
        *args,
        **kwargs,
    ):
        extra_columns = []
        if chapter:
            extra_columns.extend(
                [
                    ("chapter", tables.Column("Chapter")),
                    ("chapter.region", tables.Column("Region")),
                ]
            )
        kwargs["extra_columns"] = extra_columns
        super().__init__(*args, **kwargs)
