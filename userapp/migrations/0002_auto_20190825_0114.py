# Generated by Django 2.1.7 on 2019-08-24 17:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='citizen',
            name='account',
        ),
        migrations.RemoveField(
            model_name='citizen',
            name='password',
        ),
        migrations.RemoveField(
            model_name='firefighter',
            name='account',
        ),
        migrations.RemoveField(
            model_name='firefighter',
            name='password',
        ),
        migrations.AddField(
            model_name='citizen',
            name='user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='firefighter',
            name='user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
