# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0002_auto_20150227_1134'),
    ]

    operations = [
        migrations.CreateModel(
            name='Affiliation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('department', models.ForeignKey(to='grading.Department')),
                ('profile', models.ForeignKey(to='grading.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='profile',
            name='department',
        ),
        migrations.AlterField(
            model_name='course_session',
            name='day',
            field=models.CharField(max_length=1, choices=[('SUN', 'Sunday'), ('MON', 'Monday'), ('TUES', 'Tuesday'), ('WED', 'Wednesday'), ('THURS', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='term',
            name='season',
            field=models.CharField(max_length=10, choices=[('FL', 'Fall'), ('SP', 'Spring'), ('WT', 'Winter'), ('SM', 'Summer')]),
            preserve_default=True,
        ),
    ]
