# Generated by Django 4.2.10 on 2024-02-18 17:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mailing", "0005_remove_client_utc_offset_client_timezone_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="phone_number",
            field=models.PositiveBigIntegerField(),
        ),
    ]
