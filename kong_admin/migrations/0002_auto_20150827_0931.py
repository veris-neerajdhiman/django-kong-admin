# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield2.fields


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pluginconfigurationfield',
            name='configuration',
        ),
        migrations.AddField(
            model_name='pluginconfigurationreference',
            name='value',
            field=jsonfield2.fields.JSONField(default={}),
        ),
        migrations.DeleteModel(
            name='PluginConfigurationField',
        ),
    ]
