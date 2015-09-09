# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0002_auto_20150827_0931'),
    ]

    operations = [
        migrations.AddField(
            model_name='pluginconfigurationreference',
            name='plugin',
            field=models.IntegerField(default=12),
        ),
        migrations.AlterUniqueTogether(
            name='pluginconfigurationreference',
            unique_together=set([('plugin', 'api')]),
        ),
        migrations.RemoveField(
            model_name='pluginconfigurationreference',
            name='name',
        ),
    ]
