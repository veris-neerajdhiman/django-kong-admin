# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from faker import Factory
from faker.providers import BaseProvider

# Initialize fake
fake = Factory.create()


# Create a provider for API Names (TODO: This is taken copy-paste from python-kong. Fix duplication!)
# WTF: This is so small and prone to changes with respect to python-kong that I find it okay to copy it here. You
# can see this more as configuration.
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
        t = fake.lexify('??????ėčń')  # Add unicode bomb, congrats, your code survives it. Keep the bomb :-)
        return t

fake.add_provider(APIInfoProvider)
fake.add_provider(ConsumerInfoProvider)
