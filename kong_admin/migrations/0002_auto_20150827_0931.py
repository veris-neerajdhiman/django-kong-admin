# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
# import jsonfield2.fields 
import django.contrib.postgres.fields.jsonb



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
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
        migrations.DeleteModel(
            name='PluginConfigurationField',
        ),
    ]