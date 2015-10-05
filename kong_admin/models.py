# -*- coding: utf-8 -*-
import logging

from six import python_2_unicode_compatible
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django_enumfield import enum
from jsonfield2 import JSONField, JSONAwareManager

from .enums import Plugins
from .validators import name_validator

logger = logging.getLogger(__name__)


class KongProxyModel(models.Model):
    kong_id = models.UUIDField(null=True, blank=True, editable=False)

    created_at = models.DateTimeField(_('created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated'), auto_now=True)
    synchronized = models.BooleanField(default=False)
    synchronized_at = models.DateTimeField(_('synchronized'), null=True, blank=True, editable=False)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class APIReference(KongProxyModel):
    upstream_url = models.URLField(help_text=_(
        'The base target URL that points to your API server, this URL will be used for proxying requests. For example, '
        'https://mockbin.com.'))
    name = models.CharField(
        null=True, blank=True, unique=True, max_length=32, default=None, validators=[name_validator], help_text=_(
            'The API name. If none is specified, will default to the request_host or request_path.'))
    request_host = models.CharField(null=True, blank=True, unique=True, max_length=32, default=None, help_text=_(
        'The public DNS address that points to your API. For example, mockbin.com. At least request_host or '
        'request_path or both should be specified.'))
    request_path = models.CharField(null=True, blank=True, max_length=32, default=None, help_text=_(
        'The public path that points to your API. For example, /someservice. At least request_host or request_path or '
        'both should be specified.'))
    preserve_host = models.BooleanField(default=False, help_text=_(
        'Preserves the original Host header sent by the client, instead of replacing it with the hostname of the '
        'upstream_url. By default is false.'))
    strip_request_path = models.BooleanField(default=False, help_text=_(
        'Strip the request_path value before proxying the request to the final API. For example a request made to '
        '/someservice/hello will be resolved to upstream_url/hello. By default is false.'))
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('API Reference')
        verbose_name_plural = _('API References')

    def __str__(self):
        result = self.upstream_url if not self.name else '%s (%s)' % (self.name, self.upstream_url)
        return str(result)

    def clean(self):
        self.name = self.name or None  # Don't store empty strings
        self.request_host = self.request_host or None  # Don't store empty strings
        self.request_path = self.request_path or None  # Don't store empty strings

        if not self.request_host and not self.request_path:
            raise ValidationError('At least one of the parameters "request_host" and "request_path" should be set')

        if self.synchronized_at and not self.kong_id:
            raise ValidationError('There should be an kong_id parameter')

        if self.kong_id and not self.synchronized_at:
            raise ValidationError('There should be a synchronized_at parameter')


@python_2_unicode_compatible
class PluginConfigurationReference(KongProxyModel):
    api = models.ForeignKey(APIReference, related_name='plugins', help_text=_(
        'The API on which to add a plugin configuration'))
    consumer = models.ForeignKey('ConsumerReference', null=True, blank=True, related_name='plugins', help_text=_(
        'The consumer that overrides the existing settings for this specific consumer on incoming requests.'))
    plugin = enum.EnumField(Plugins, default=Plugins.REQUEST_SIZE_LIMITING, help_text=_(
        'The name of the Plugin that\'s going to be added. Currently the Plugin must be installed in every Kong '
        'instance separately.'))
    enabled = models.BooleanField(default=True)
    config = JSONField(default={}, help_text=_(
        'The configuration properties for the Plugin which can be found on the plugins documentation page in the '
        'Plugin Gallery.'))

    objects = JSONAwareManager(json_fields=['config'])

    class Meta:
        verbose_name = _('Plugin Configuration Reference')
        verbose_name_plural = _('Plugin Configuration References')
        unique_together = [('plugin', 'api')]

    def __str__(self):
        return str(Plugins.label(self.plugin))


@python_2_unicode_compatible
class ConsumerReference(KongProxyModel):
    username = models.CharField(null=True, blank=True, unique=True, max_length=32, help_text=_(
        'The username of the consumer. You must send either this field or custom_id with the request.'))
    custom_id = models.CharField(null=True, blank=True, unique=True, max_length=48, help_text=_(
        'Field for storing an existing ID for the consumer, useful for mapping Kong with users in your existing '
        'database. You must send either this field or username with the request.'))
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Consumer Reference')
        verbose_name_plural = _('Consumer References')

    def __str__(self):
        return self.username or self.custom_id

    def clean(self):
        self.username = self.username or None  # Don't store empty strings
        self.custom_id = self.custom_id or None  # Don't store empty strings

        if not self.username and not self.custom_id:
            raise ValidationError('At least one of the parameters "username" and "custom_id" should be set')


class ConsumerAuthentication(KongProxyModel):
    consumer = models.ForeignKey(ConsumerReference)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class BasicAuthReference(ConsumerAuthentication):
    username = models.CharField(unique=True, max_length=32, help_text=_(
        'The username to use in the Basic Authentication'))
    password = models.CharField(max_length=40, help_text=_('The password to use in the Basic Authentication'))

    class Meta:
        verbose_name = _('Basic Auth Reference')
        verbose_name_plural = _('Basic Auth References')

    def __str__(self):
        return 'BasicAuthReference(consumer: %s, username: %s)' % (self.consumer, self.username)


@python_2_unicode_compatible
class KeyAuthReference(ConsumerAuthentication):
    key = models.TextField(help_text=_(
        'You can optionally set your own unique key to authenticate the client. If missing, the plugin will generate '
        'one.'))

    class Meta:
        verbose_name = _('Key Auth Reference')
        verbose_name_plural = _('Key Auth References')

    def __str__(self):
        key = self.key
        if len(key) > 16:
            key = '%s...' % key[:16]
        return 'KeyAuthReference(consumer: %s, key: %s)' % (self.consumer, key)


@python_2_unicode_compatible
class OAuth2Reference(ConsumerAuthentication):
    name = models.CharField(unique=True, max_length=32, help_text=_(
        'The name to associate to the credential. In OAuth 2.0 this would be the application name.'))
    redirect_uri = models.URLField(help_text=_(
        'The URL in your app where users will be sent after authorization (RFC 6742 Section 3.1.2)'))
    client_id = models.CharField(null=True, blank=True, unique=True, max_length=64, help_text=_(
        'You can optionally set your own unique client_id. If missing, the plugin will generate one.'))
    client_secret = models.TextField(null=True, blank=True, help_text=_(
        'You can optionally set your own unique client_secret. If missing, the plugin will generate one.'))

    class Meta:
        verbose_name = _('OAuth2 Reference')
        verbose_name_plural = _('OAuth2 References')

    def __str__(self):
        return 'OAuth2Reference(name: %s)' % self.name

    def clean(self):
        self.client_id = self.client_id or None  # Don't store empty strings
        self.client_secret = self.client_secret or None  # Don't store empty strings
