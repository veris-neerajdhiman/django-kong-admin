# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from .factory import get_api_sync_engine, get_consumer_sync_engine
from .models import APIReference, ConsumerReference, PluginConfigurationReference


def publish_api(client, obj):
    obj = get_api_sync_engine().publish(client, obj)
    if not obj.enabled:
        obj.enabled = True
        APIReference.objects.filter(id=obj.id).update(enabled=obj.enabled)
    return obj


def withdraw_api(client, obj):
    obj = get_api_sync_engine().withdraw(client, obj)
    if obj.enabled:
        obj.enabled = False
        APIReference.objects.filter(id=obj.id).update(enabled=obj.enabled)
    return obj


def synchronize_api(client, obj, toggle=False):
    if (toggle and obj.enabled) or (not toggle and not obj.enabled):
        return withdraw_api(client, obj)
    return publish_api(client, obj)


def synchronize_apis(client, queryset=None):
    return get_api_sync_engine().synchronize(client, queryset=queryset, delete=True)


def publish_plugin_configuration(client, obj):
    obj = get_api_sync_engine().plugins().publish(client, obj)
    return obj


def withdraw_plugin_configuration(client, obj):
    obj = get_api_sync_engine().plugins().withdraw(client, obj)
    return obj


def enable_plugin_configuration(client, obj, enabled=True):
    obj.enabled = enabled
    obj = get_api_sync_engine().plugins().publish(client, obj)

    # Updated enabled state without triggering another save
    PluginConfigurationReference.objects.filter(id=obj.id).update(enabled=obj.enabled)

    return obj


def synchronize_plugin_configuration(client, obj, toggle=False):
    enabled = not obj.enabled if toggle else obj.enabled
    return enable_plugin_configuration(client, obj, enabled=enabled)


def synchronize_plugin_configurations(client, queryset=None):
    return get_api_sync_engine().plugins().synchronize(client, queryset=queryset, delete=True)


def publish_consumer(client, obj):
    obj = get_consumer_sync_engine().publish(client, obj)
    if not obj.enabled:
        obj.enabled = True
        ConsumerReference.objects.filter(id=obj.id).update(enabled=obj.enabled)


def withdraw_consumer(client, obj):
    obj = get_consumer_sync_engine().withdraw(client, obj)
    if obj.enabled:
        obj.enabled = False
        ConsumerReference.objects.filter(id=obj.id).update(enabled=obj.enabled)


def synchronize_consumer(client, obj, toggle=False):
    if (toggle and obj.enabled) or (not toggle and not obj.enabled):
        return withdraw_consumer(client, obj)
    return publish_consumer(client, obj)


def synchronize_consumers(client, queryset=None):
    return get_consumer_sync_engine().synchronize(client, queryset=queryset, delete=True)
