from django.apps import AppConfig
from watson import search as watson


class UsersConfig(AppConfig):
    name = "users"
    verbose_name = "Users"

    def ready(self):
        """Override this to put in:
        Users system checks
        Users signal registration
        """
        try:
            import users.signals  # noqa F401
        except ImportError:
            pass
        model = self.get_model("User")
        # When this is updated need to run: python manage.py buildwatson
        watson.register(
            model,
            fields=[
                "name",
                "badge_number",
                "id",
                "username",
                "first_name",
                "last_name",
                "preferred_pronouns",
                "preferred_name",
                "nickname",
                "maiden_name",
                "email",
                "email_school",
                "chapter__name",
            ],
        )
