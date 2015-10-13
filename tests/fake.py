# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from faker import Factory
from faker.providers import BaseProvider

# Initialize fake
fake = Factory.create()


class APIInfoProvider(BaseProvider):
    def api_name(self):
        return fake.name().replace(' ', '')

    def api_path(self):
        path = fake.uri_path()
        if not path.startswith('/'):
            path = '/%s' % path
        return path


class ConsumerInfoProvider(BaseProvider):
    def consumer_name(self):
        t = fake.lexify('??????ėčń')
        return t

fake.add_provider(APIInfoProvider)
fake.add_provider(ConsumerInfoProvider)
