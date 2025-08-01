from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.views import (
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetView,
    PasswordResetDoneView,
)
from oauth2_provider import urls as oauth2_urls
from allauth.account.views import LogoutView
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from material.frontend.urls import modules
from core.views import HomeView
from core.address import ZipCodeAutocomplete
from users.views import UserLookupLoginView
from django.views import defaults as default_views


def home_redirect(request):
    return redirect("http://127.0.0.1")


urlpatterns = [
    path("django_plotly_dash/", include("django_plotly_dash.urls")),
    path("o/", include(oauth2_urls)),
    url(
        r"^zipcode-autocomplete/$",
        ZipCodeAutocomplete.as_view(),
        name="zipcode-autocomplete",
    ),
    url(r"^$", HomeView.as_view(template_name="pages/home.html"), name="home"),
    url(r"^", include("allauth_2fa.urls")),
    url(
        r"^favicon\.ico$",
        RedirectView.as_view(
            url=settings.STATIC_URL + "images/favicon.png", permanent=True
        ),
    ),
    url(r"^wp-content/*", home_redirect),
    url(
        r"^about/$",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    url(r"^help/$", TemplateView.as_view(template_name="pages/help.html"), name="help"),
    url(
        r"^electronic_terms/$",
        TemplateView.as_view(template_name="pages/electronic_terms.html"),
        name="electronic_terms",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="account/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    url(
        r"^reset/done/$",
        PasswordResetCompleteView.as_view(
            template_name="account/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    url(
        r"^password_reset/$",
        PasswordResetView.as_view(template_name="account/password_reset.html"),
        name="password_reset",
    ),
    url(
        r"^password_reset/done/$",
        PasswordResetDoneView.as_view(template_name="account/password_reset_done.html"),
        name="password_reset_done",
    ),
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),
    # User management
    url(r"^users/", include("users.urls", namespace="users")),
    url(r"^accounts/login/$", UserLookupLoginView.as_view(), name="login"),
    url(r"^accounts/logout/$", LogoutView.as_view(), name="logout"),
    url(r"^accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    url(r"^$", RedirectView.as_view(url="/workflow/", permanent=False)),
    url(r"^report_builder/", include("report_builder.urls")),
    url(r"", include((modules.urls))),
    url(r"^ckeditor/", include("ckeditor_uploader.urls")),
    path("email-signals/", include("email_signals.urls")),
    url(r"^terms/", include("termsandconditions.urls")),
    url(
        r"^privacy/",
        RedirectView.as_view(url="/terms/view/privacy/", permanent=True),
        name="privacy",
    ),
    url(
        r"^eula/",
        RedirectView.as_view(url="/terms/view/eula/", permanent=True),
        name="eula",
    ),
    url(r"^regions/", include("regions.urls", namespace="regions")),
    url(r"^chapters/", include("chapters.urls", namespace="chapters")),
    url(r"^events/", include("events.urls", namespace="events")),
    url(r"^jobs/", include("jobs.urls", namespace="jobs")),
    url(r"^notes/", include("notes.urls", namespace="notes")),
    url(r"^goals/", include("objectives.urls", namespace="objectives")),
    url(r"^trainings/", include("trainings.urls", namespace="trainings")),
    url(r"^finances/", include("finances.urls", namespace="finances")),
    url(r"^scores/", include("scores.urls", namespace="scores")),
    url(r"^submissions/", include("submissions.urls", namespace="submissions")),
    url(r"^surveys/", include("surveys.urls", namespace="surveys")),
    url(r"^forms/", include("forms.urls", namespace="forms")),
    url(r"^tasks/", include("tasks.urls", namespace="tasks")),
    url(r"^ballots/", include("ballots.urls", namespace="ballots")),
    url(
        r"^rmp/$",
        RedirectView.as_view(pattern_name="forms:rmp", permanent=True),
        name="rmp",
    ),
    url(
        r"^initiation/$",
        RedirectView.as_view(pattern_name="forms:initiation", permanent=True),
    ),
    url(
        r"^officer/$",
        RedirectView.as_view(pattern_name="forms:officer", permanent=True),
    ),
    url(
        r"^status/$", RedirectView.as_view(pattern_name="forms:status", permanent=True)
    ),
    url(
        r"^pledgeform/$",
        RedirectView.as_view(pattern_name="forms:pledgeform", permanent=True),
    ),
    url(
        r"^pledgeform-alt/$",
        RedirectView.as_view(pattern_name="forms:pledgeform-alt", permanent=True),
    ),
    url(
        r"^report/$",
        RedirectView.as_view(
            pattern_name="viewflow:forms:hseducation:start", permanent=False
        ),
    ),
    url(
        r"^education/$",
        RedirectView.as_view(
            pattern_name="viewflow:forms:hseducation:start", permanent=True
        ),
    ),
    url(
        r"^nme-program/$",
        RedirectView.as_view(
            pattern_name="viewflow:forms:pledgeprogramprocess:start", permanent=True
        ),
    ),
    url(
        r"^conventionform/$",
        RedirectView.as_view(
            pattern_name="viewflow:forms:convention:start", permanent=True
        ),
        name="conventionform",
    ),
    url(
        r"^osmform/$",
        RedirectView.as_view(pattern_name="viewflow:forms:osm:start", permanent=True),
        name="osmform",
    ),
    url(
        r"^alumniexclusionform/$",
        RedirectView.as_view(
            pattern_name="viewflow:forms:alumniexclusion:start", permanent=True
        ),
        name="alumniexclusion",
    ),
    url(
        r"^gear/$",
        RedirectView.as_view(pattern_name="submissions:gear", permanent=True),
        name="gear",
    ),
    url(
        r"^update/$",
        RedirectView.as_view(pattern_name="users:lookup_search", permanent=True),
        name="update_lookup",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(
            r"^400/$",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        url(
            r"^403/$",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        url(
            r"^404/$",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        url(r"^500/$", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            url(r"^__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns

if settings.DEBUG or "staging" in settings.SETTINGS_MODULE:
    urlpatterns += [
        url(r"^herald/", include("herald.urls")),
    ]
