# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield2.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIReference',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('kong_id', models.UUIDField(editable=False, blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, blank=True, null=True, verbose_name='synchronized')),
                ('upstream_url', models.URLField()),
                ('name', models.CharField(unique=True, default=None, blank=True, max_length=32, null=True)),
                ('inbound_dns', models.CharField(unique=True, default=None, blank=True, max_length=32, null=True)),
                ('path', models.CharField(default=None, blank=True, max_length=32, null=True)),
                ('strip_path', models.BooleanField(default=False)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'API References',
                'verbose_name': 'API Reference',
            },
        ),
        migrations.CreateModel(
            name='BasicAuthReference',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('kong_id', models.UUIDField(editable=False, blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, blank=True, null=True, verbose_name='synchronized')),
                ('username', models.CharField(unique=True, max_length=32)),
                ('password', models.CharField(max_length=40)),
            ],
            options={
                'verbose_name_plural': 'Basic Auth References',
                'verbose_name': 'Basic Auth Reference',
            },
        ),
        migrations.CreateModel(
            name='ConsumerReference',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('kong_id', models.UUIDField(editable=False, blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, blank=True, null=True, verbose_name='synchronized')),
                ('username', models.CharField(unique=True, blank=True, max_length=32, null=True)),
                ('custom_id', models.CharField(unique=True, blank=True, max_length=48, null=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Consumer References',
                'verbose_name': 'Consumer Reference',
            },
        ),
        migrations.CreateModel(
            name='KeyAuthReference',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('kong_id', models.UUIDField(editable=False, blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, blank=True, null=True, verbose_name='synchronized')),
                ('key', models.TextField()),
                ('consumer', models.ForeignKey(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name_plural': 'Key Auth References',
                'verbose_name': 'Key Auth Reference',
            },
        ),
        migrations.CreateModel(
            name='OAuth2Reference',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('kong_id', models.UUIDField(editable=False, blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, blank=True, null=True, verbose_name='synchronized')),
                ('name', models.CharField(unique=True, max_length=32)),
                ('redirect_uri', models.URLField()),
                ('client_id', models.CharField(unique=True, blank=True, max_length=64, null=True)),
                ('client_secret', models.TextField(blank=True, null=True)),
                ('consumer', models.ForeignKey(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name_plural': 'OAuth2 References',
                'verbose_name': 'OAuth2 Reference',
            },
        ),
        migrations.CreateModel(
            name='PluginConfigurationReference',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('kong_id', models.UUIDField(editable=False, blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, blank=True, null=True, verbose_name='synchronized')),
                ('plugin', models.IntegerField(default=13)),
                ('enabled', models.BooleanField(default=True)),
                ('config', jsonfield2.fields.JSONField(default={})),
                ('api', models.ForeignKey(to='kong_admin.APIReference', related_name='plugins')),
                ('consumer', models.ForeignKey(null=True, blank=True, related_name='plugins', to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name_plural': 'Plugin Configuration References',
                'verbose_name': 'Plugin Configuration Reference',
            },
        ),
        migrations.AddField(
            model_name='basicauthreference',
            name='consumer',
            field=models.ForeignKey(to='kong_admin.ConsumerReference'),
        ),
        migrations.AlterUniqueTogether(
            name='pluginconfigurationreference',
            unique_together=set([('plugin', 'api')]),
        ),
    ]
