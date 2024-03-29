# Generated by Django 4.2.10 on 2024-02-18 16:10

from django.db import migrations, models
import django.db.models.deletion
import mailing.models


class Migration(migrations.Migration):
    dependencies = [
        ("mailing", "0004_alter_mailing_tags_filter"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="client",
            name="utc_offset",
        ),
        migrations.AddField(
            model_name="client",
            name="timezone",
            field=models.CharField(default="UTC", max_length=100),
        ),
        migrations.AlterField(
            model_name="client",
            name="tag",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="message",
            name="client_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_messages",
                to="mailing.client",
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="sent_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="message",
            name="status",
            field=models.CharField(
                default=mailing.models.MessageStatus["WAITING"], max_length=50
            ),
        ),
    ]
