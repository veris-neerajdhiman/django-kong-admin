# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import factory

from kong_admin.models import APIReference, ConsumerReference, PluginConfigurationReference, PluginConfigurationField, \
    BasicAuthReference, KeyAuthReference, OAuth2Reference
from kong_admin.enums import Plugins

from .fake import fake


class APIReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = APIReference

    target_url = factory.Sequence(lambda n: fake.url().encode('utf-8'))


class PluginConfigurationReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = PluginConfigurationReference

    api = factory.SubFactory(APIReferenceFactory)
    name = Plugins.ratelimiting.name


class PluginConfigurationFieldFactory(factory.DjangoModelFactory):
    class Meta:
        model = PluginConfigurationField

    configuration = factory.SubFactory(PluginConfigurationReferenceFactory)
    property = 'second'
    value = 1


class ConsumerReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = ConsumerReference


class BasicAuthReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = BasicAuthReference

    username = factory.Sequence(lambda n: fake.user_name().encode('utf-8'))
    password = factory.Sequence(lambda n: fake.password(
        length=10, special_chars=True, digits=True, upper_case=True, lower_case=True).encode('utf-8'))


class KeyAuthReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = KeyAuthReference

    key = factory.Sequence(lambda n: fake.password(
        length=40, special_chars=True, digits=True, upper_case=True, lower_case=True).encode('utf-8'))


class OAuth2ReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = OAuth2Reference

    name = factory.Sequence(lambda n: fake.word().encode('utf-8'))
    redirect_uri = factory.Sequence(lambda n: fake.uri().encode('utf-8'))

__all__ = [APIReferenceFactory, PluginConfigurationReferenceFactory, PluginConfigurationFieldFactory,
           ConsumerReferenceFactory, BasicAuthReferenceFactory, KeyAuthReferenceFactory, OAuth2ReferenceFactory]
