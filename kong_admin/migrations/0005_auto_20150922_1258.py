# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0004_auto_20150909_0826'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apireference',
            old_name='inbound_dns',
            new_name='request_host',
        ),
        migrations.RenameField(
            model_name='apireference',
            old_name='path',
            new_name='request_path',
        ),
        migrations.RemoveField(
            model_name='apireference',
            name='strip_path',
        ),
    ]
