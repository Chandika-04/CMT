# Generated by Django 3.2.15 on 2024-04-12 00:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0032_auto_20240411_1718"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberupdate",
            name="unsubscribe_email",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="memberupdate",
            name="unsubscribe_paper_gear",
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
