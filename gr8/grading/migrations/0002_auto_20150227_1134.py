# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='season',
            field=models.CharField(choices=[('Fall', 'Fall'), ('Spring', 'Spring'), ('Winter', 'Winter'), ('Summer', 'Summer')], max_length=10),
            preserve_default=True,
        ),
    ]
