# Generated by Django 2.1.9 on 2021-06-08 13:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210603_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]