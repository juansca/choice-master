# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-25 03:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chm', '0002_auto_20161025_0304'),
    ]

    operations = [
        migrations.CreateModel(
            name='XMLFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='media')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chm.Topic')),
            ],
        ),
    ]