# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0005_auto_20150922_1258'),
    ]

    operations = [
        migrations.AddField(
            model_name='apireference',
            name='preserve_host',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='apireference',
            name='strip_request_path',
            field=models.BooleanField(default=False),
        ),
    ]
