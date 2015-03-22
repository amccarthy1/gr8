# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0003_auto_20150309_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='capacity',
            field=models.IntegerField(default=40),
            preserve_default=False,
        ),
    ]
