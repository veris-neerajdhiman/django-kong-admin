# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0003_auto_20150909_0756'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pluginconfigurationreference',
            old_name='value',
            new_name='config',
        ),
        migrations.AlterField(
            model_name='pluginconfigurationreference',
            name='plugin',
            field=models.IntegerField(default=13),
        ),
    ]
