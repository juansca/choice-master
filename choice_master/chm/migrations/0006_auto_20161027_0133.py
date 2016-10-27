# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-27 01:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chm', '0005_auto_20161026_1038'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionOnQuiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('not_answered', 'not_answered'), ('wrong', 'wrong'), ('right', 'right')], default='not_answered', max_length=20)),
                ('question', models.ManyToManyField(to='chm.Question')),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('seconds_per_question', models.IntegerField()),
                ('topics', models.ManyToManyField(to='chm.Topic')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='questiononquiz',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chm.Quiz'),
        ),
    ]
