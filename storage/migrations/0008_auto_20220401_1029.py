# Generated by Django 3.2.12 on 2022-04-01 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0007_alter_graphiccard_price_was_updated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='graphiccard',
            name='price_was_updated',
        ),
        migrations.AddField(
            model_name='graphiccard',
            name='price_notification_request',
            field=models.BooleanField(blank=True, default=False, verbose_name='уведомить пользователей об изменении цены'),
        ),
    ]
