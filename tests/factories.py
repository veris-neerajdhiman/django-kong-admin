# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import factory

from kong_admin.models import APIReference, ConsumerReference, PluginConfigurationReference, PluginConfigurationField
from kong_admin.enums import Plugins

class APIReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = APIReference

    target_url = factory.Sequence(lambda n: ('http://mockbin%d.com' % n).encode('utf-8'))


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


__all__ = [APIReferenceFactory, PluginConfigurationReferenceFactory, PluginConfigurationFieldFactory,
           ConsumerReferenceFactory]
