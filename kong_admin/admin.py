# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
# from jsonfield2.fields import JSONField
from django.contrib.postgres.fields import JSONField


from .models import APIReference, PluginConfigurationReference, ConsumerReference, \
    BasicAuthReference, KeyAuthReference, OAuth2Reference
from .views import synchronize_api_reference, synchronize_api_references, synchronize_consumer_reference, \
    synchronize_consumer_references
from .contrib import ActionButtonModelAdmin
from .widgets import JSONWidget


def get_toggle_enable_caption(obj):
    return 'Disable' if obj.enabled else 'Enable'


class PluginConfigurationReferenceInline(admin.StackedInline):
    model = PluginConfigurationReference
    extra = 0
    fields = ('plugin', 'config', 'enabled', 'consumer')
    formfield_overrides = {
        JSONField: {'widget': JSONWidget(mode='json', width='800px', height='180px', theme='twilight')},
    }


class APIReferenceAdmin(ActionButtonModelAdmin):
    list_display = ('upstream_url', 'name', 'request_host', 'preserve_host', 'request_path', 'strip_request_path',
                    'enabled', 'synchronized', 'kong_id')
    list_display_buttons = [{
        'caption': 'Synchronize',
        'url': 'sync-api-ref/',
        'view': synchronize_api_reference
    }, {
        'caption': get_toggle_enable_caption,
        'url': 'toggle-enable/',
        'view': lambda request, pk: synchronize_api_reference(request, pk, toggle_enable=True)
    }]
    action_buttons = [{
        'caption': 'Synchronize all',
        'url': 'sync-api-refs/',
        'view': synchronize_api_references
    }]
    list_select_related = True
    fieldsets = (
        (None, {
            'fields': ('upstream_url', 'name', 'enabled')
        }),
        (_('Host'), {
            'fields': ('request_host', 'preserve_host')
        }),
        (_('Path'), {
            'fields': ('request_path', 'strip_request_path')
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [
        PluginConfigurationReferenceInline
    ]
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(APIReference, APIReferenceAdmin)


class BasicAuthInline(admin.StackedInline):
    model = BasicAuthReference
    extra = 0
    fields = ('username', 'password')


class KeyAuthInline(admin.StackedInline):
    model = KeyAuthReference
    extra = 0
    fields = ('key',)


class OAuthInline(admin.StackedInline):
    model = OAuth2Reference
    extra = 0
    fields = ('name', 'redirect_uri', 'client_id', 'client_secret')


class ConsumerReferenceAdmin(ActionButtonModelAdmin):
    list_display = ('username_or_custom_id', 'enabled', 'synchronized', 'kong_id')
    list_display_buttons = [{
        'caption': 'Synchronize',
        'url': 'sync-consumer-ref/',
        'view': synchronize_consumer_reference
    }, {
        'caption': get_toggle_enable_caption,
        'url': 'toggle-enable/',
        'view': lambda request, pk: synchronize_consumer_reference(request, pk, toggle_enable=True)
    }]
    action_buttons = [{
        'caption': 'Synchronize all',
        'url': 'sync-consumer-refs/',
        'view': synchronize_consumer_references
    }]
    list_select_related = True
    fieldsets = (
        (None, {
            'fields': ('username', 'custom_id', 'enabled')
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [
        BasicAuthInline,
        KeyAuthInline,
        OAuthInline
    ]

    def username_or_custom_id(self, obj):
        return obj.username or obj.custom_id

admin.site.register(ConsumerReference, ConsumerReferenceAdmin)
