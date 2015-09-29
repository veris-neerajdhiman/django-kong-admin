from __future__ import unicode_literals, print_function
import uuid

from django.test import TestCase

from kong_admin import models
from kong_admin import logic
from kong_admin.factory import get_kong_client
from kong_admin.enums import Plugins


from .factories import APIReferenceFactory, PluginConfigurationReferenceFactory, ConsumerReferenceFactory, \
    BasicAuthReferenceFactory, KeyAuthReferenceFactory, OAuth2ReferenceFactory
from .fake import fake
from kong_admin.models import PluginConfigurationReference


class APIReferenceLogicTestCase(TestCase):
    def setUp(self):
        self.client = get_kong_client()
        self._cleanup_api = []

    def tearDown(self):
        self.client.close()

        for api_ref in self._cleanup_api:
            self.assertTrue(isinstance(api_ref, models.APIReference))
            api_ref = models.APIReference.objects.get(id=api_ref.id)  # reloads!!
            logic.withdraw_api(self.client, api_ref)

    def test_sync_incomplete_api(self):
        # Create incomplete api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Try to sync, expect an error
        with self.assertRaises(ValueError):
            logic.synchronize_api(self.client, api_ref)

        self.assertFalse(api_ref.synchronized)

        # Fix api_ref
        api_ref.request_host = fake.domain_name()
        api_ref.save()

        # Sync again
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['upstream_url'], api_ref.upstream_url)
        self.assertEqual(result['request_host'], api_ref.request_host)

    def test_sync_api(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Sync
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['upstream_url'], api_ref.upstream_url)
        self.assertEqual(result['request_host'], api_ref.request_host)

    def test_sync_updated_api(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['upstream_url'], api_ref.upstream_url)
        self.assertEqual(result['request_host'], api_ref.request_host)
        self.assertEqual(result['name'], api_ref.request_host)

        # Update
        new_name = fake.api_name()
        self.assertNotEqual(new_name, api_ref.name)
        api_ref.name = new_name
        api_ref.save()

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['upstream_url'], api_ref.upstream_url)
        self.assertEqual(result['request_host'], api_ref.request_host)
        self.assertEqual(result['name'], new_name)

    def test_withdraw_api(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['upstream_url'], api_ref.upstream_url)
        self.assertEqual(result['request_host'], api_ref.request_host)

        # Store kong_id
        kong_id = api_ref.kong_id

        # You can delete afterwards
        logic.withdraw_api(self.client, api_ref)
        self.assertFalse(api_ref.synchronized)

        # Check kong
        with self.assertRaises(ValueError):
            _ = self.client.apis.retrieve(kong_id)

    def test_delete_api(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['upstream_url'], api_ref.upstream_url)
        self.assertEqual(result['request_host'], api_ref.request_host)

        # You can delete afterwards
        api_kong_id = api_ref.kong_id
        api_ref.delete()

        # Check kong
        with self.assertRaises(ValueError):
            _ = self.client.apis.retrieve(api_kong_id)

    def test_sync_plugin_configuration_before_api(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Attempt to publish
        with self.assertRaises(ValueError):
            logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

    def test_sync_plugin_configuration_without_fields(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Check
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['upstream_url'], api_ref.upstream_url)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref, config={})

        # Attempt to publish
        with self.assertRaises(ValueError):
            logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

    def test_sync_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Check
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['upstream_url'], api_ref.upstream_url)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], Plugins.label(plugin_configuration_ref.plugin))

    def test_withdraw_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], Plugins.label(plugin_configuration_ref.plugin))

        # Withdraw plugin_configuration
        logic.withdraw_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        with self.assertRaises(ValueError):
            _ = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)

    def test_delete_synchronized_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], Plugins.label(plugin_configuration_ref.plugin))

        # Delete plugin_configuration
        plugin_configuration_kong_id = plugin_configuration_ref.kong_id
        plugin_configuration_ref.delete()

        # Check
        with self.assertRaises(ValueError):
            _ = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_kong_id)

    def test_disable_synchronized_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], Plugins.label(plugin_configuration_ref.plugin))
        self.assertTrue(result['enabled'])

        # Update plugin_configuration
        logic.enable_plugin_configuration(self.client, plugin_configuration_ref, enabled=False)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], Plugins.label(plugin_configuration_ref.plugin))
        self.assertFalse(result['enabled'])

    def test_update_synchronized_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], Plugins.label(plugin_configuration_ref.plugin))
        self.assertEqual(result['config']['second'], plugin_configuration_ref.config['second'])

        # Update plugin_configuration
        new_value = 5
        self.assertNotEqual(new_value, plugin_configuration_ref.config['second'])
        plugin_configuration_ref.config['second'] = new_value
        plugin_configuration_ref.save()
        logic.publish_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], Plugins.label(plugin_configuration_ref.plugin))
        self.assertEqual(result['config']['second'], plugin_configuration_ref.config['second'])

    def _cleanup_afterwards(self, api_ref):
        self._cleanup_api.append(api_ref)
        return api_ref


class ConsumerReferenceLogicTestCase(TestCase):
    def setUp(self):
        self.client = get_kong_client()
        self._cleanup_consumers = []

    def tearDown(self):
        self.client.close()

        for consumer_ref in self._cleanup_consumers:
            self.assertTrue(isinstance(consumer_ref, models.ConsumerReference))
            consumer_ref = models.ConsumerReference.objects.get(id=consumer_ref.id)  # reloads!!
            logic.withdraw_consumer(self.client, consumer_ref)

    def test_incomplete_consumer(self):
        # Create incomplete consumer_ref
        consumer_ref = ConsumerReferenceFactory()

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Try to sync, expect an error
        with self.assertRaises(ValueError):
            logic.synchronize_consumer(self.client, consumer_ref)

        self.assertFalse(consumer_ref.synchronized)

        # Fix consumer_ref
        consumer_ref.username = fake.consumer_name()
        consumer_ref.save()

        # Sync again
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check kong
        result = self.client.consumers.retrieve(consumer_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], consumer_ref.username)

    def test_sync_consumer(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Sync
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check kong
        result = self.client.consumers.retrieve(consumer_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], consumer_ref.username)

    def test_sync_updated_consumer(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check kong
        result = self.client.consumers.retrieve(consumer_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], consumer_ref.username)

        # Update
        new_name = fake.consumer_name()
        self.assertNotEqual(new_name, consumer_ref.username)
        consumer_ref.username = new_name
        consumer_ref.save()

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check kong
        result = self.client.consumers.retrieve(consumer_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], new_name)

    def test_withdraw_consumer(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check kong
        result = self.client.consumers.retrieve(consumer_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], consumer_ref.username)

        # Store kong_id
        kong_id = consumer_ref.kong_id

        # You can delete afterwards
        logic.withdraw_consumer(self.client, consumer_ref)
        self.assertFalse(consumer_ref.synchronized)

        # Check kong
        with self.assertRaises(ValueError):
            _ = self.client.consumers.retrieve(kong_id)

    def test_delete_consumer(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check kong
        result = self.client.consumers.retrieve(consumer_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], consumer_ref.username)

        # You can delete afterwards
        consumer_kong_id = consumer_ref.kong_id
        consumer_ref.delete()

        # Check kong
        with self.assertRaises(ValueError):
            _ = self.client.consumers.retrieve(consumer_kong_id)

    def test_sync_consumer_basic_auth(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check kong
        amount = self.client.consumers.basic_auth(consumer_ref.kong_id).count()
        self.assertEqual(amount, 0)

        # Create auth
        auth_ref = BasicAuthReferenceFactory(consumer=consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Reload
        auth_ref = models.BasicAuthReference.objects.get(id=auth_ref.id)
        self.assertIsNotNone(auth_ref.kong_id)

        # Check kong
        result = self.client.consumers.basic_auth(consumer_ref.kong_id).retrieve(auth_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], auth_ref.username)
        self.assertIsNotNone(result['password'])

    def test_sync_consumer_multiple_basic_auth(self):
        amount = 3

        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Create auths
        auths = []
        for i in range(amount):
            auths.append(BasicAuthReferenceFactory(consumer=consumer_ref))

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check
        self.assertEqual(self.client.consumers.basic_auth(consumer_ref.kong_id).count(), amount)

        # Reload
        for i in range(len(auths)):
            auths[i] = models.BasicAuthReference.objects.get(id=auths[i].id)
            self.assertIsNotNone(auths[i].kong_id)

        # Check kong
        result = self.client.consumers.basic_auth(consumer_ref.kong_id).list()
        self.assertIsNotNone(result)
        self.assertEqual(
            sorted([(uuid.UUID(r['id']), r['username']) for r in result['data']], key=lambda x: x[0]),
            sorted([(obj.kong_id, obj.username) for obj in auths], key=lambda x: x[0]))

    def test_withdraw_consumer_basic_auth(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Create auth
        auth_ref = BasicAuthReferenceFactory(consumer=consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Reload
        auth_ref = models.BasicAuthReference.objects.get(id=auth_ref.id)
        self.assertIsNotNone(auth_ref.kong_id)
        self.assertTrue(auth_ref.synchronized)

        # Withdraw
        logic.withdraw_consumer(self.client, consumer_ref)
        self.assertFalse(consumer_ref.synchronized)

        # Reload
        auth_ref = models.BasicAuthReference.objects.get(id=auth_ref.id)
        self.assertIsNone(auth_ref.kong_id)
        self.assertFalse(auth_ref.synchronized)

    def test_delete_consumer_basic_auth(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Create auth
        auth_ref1 = BasicAuthReferenceFactory(consumer=consumer_ref)
        BasicAuthReferenceFactory(consumer=consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check
        self.assertEqual(self.client.consumers.basic_auth(consumer_ref.kong_id).count(), 2)

        # Delete auth_ref1
        auth_ref1.delete()

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check
        self.assertEqual(self.client.consumers.basic_auth(consumer_ref.kong_id).count(), 1)

        # Delete consumer
        consumer_kong_id = consumer_ref.kong_id
        consumer_ref.delete()

        # Check
        with self.assertRaises(ValueError):
            self.client.consumers.basic_auth(consumer_kong_id).count()

    def test_sync_consumer_key_auth(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check kong
        amount = self.client.consumers.key_auth(consumer_ref.kong_id).count()
        self.assertEqual(amount, 0)

        # Create auth
        auth_ref = KeyAuthReferenceFactory(consumer=consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Reload
        auth_ref = models.KeyAuthReference.objects.get(id=auth_ref.id)
        self.assertIsNotNone(auth_ref.kong_id)

        # Check kong
        result = self.client.consumers.key_auth(consumer_ref.kong_id).retrieve(auth_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['key'], auth_ref.key)

    def test_sync_consumer_multiple_key_auth(self):
        amount = 3

        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Create auths
        auths = []
        for i in range(amount):
            auths.append(KeyAuthReferenceFactory(consumer=consumer_ref))

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check
        self.assertEqual(self.client.consumers.key_auth(consumer_ref.kong_id).count(), amount)

        # Reload
        for i in range(len(auths)):
            auths[i] = models.KeyAuthReference.objects.get(id=auths[i].id)
            self.assertIsNotNone(auths[i].kong_id)

        # Check kong
        result = self.client.consumers.key_auth(consumer_ref.kong_id).list()
        self.assertIsNotNone(result)
        self.assertEqual(
            sorted([(uuid.UUID(r['id']), r['key']) for r in result['data']], key=lambda x: x[0]),
            sorted([(obj.kong_id, obj.key) for obj in auths], key=lambda x: x[0]))

    def test_withdraw_consumer_key_auth(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Create auth
        auth_ref = KeyAuthReferenceFactory(consumer=consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Reload
        auth_ref = models.KeyAuthReference.objects.get(id=auth_ref.id)
        self.assertIsNotNone(auth_ref.kong_id)
        self.assertTrue(auth_ref.synchronized)

        # Withdraw
        logic.withdraw_consumer(self.client, consumer_ref)
        self.assertFalse(consumer_ref.synchronized)

        # Reload
        auth_ref = models.KeyAuthReference.objects.get(id=auth_ref.id)
        self.assertIsNone(auth_ref.kong_id)
        self.assertFalse(auth_ref.synchronized)

    def test_delete_consumer_key_auth(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Create auth
        auth_ref1 = KeyAuthReferenceFactory(consumer=consumer_ref)
        KeyAuthReferenceFactory(consumer=consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check
        self.assertEqual(self.client.consumers.key_auth(consumer_ref.kong_id).count(), 2)

        # Delete auth_ref1
        auth_ref1.delete()

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check
        self.assertEqual(self.client.consumers.key_auth(consumer_ref.kong_id).count(), 1)

        # Delete consumer
        consumer_kong_id = consumer_ref.kong_id
        consumer_ref.delete()

        # Check
        with self.assertRaises(ValueError):
            self.client.consumers.key_auth(consumer_kong_id).count()

    def test_sync_consumer_oauth2(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check kong
        amount = self.client.consumers.oauth2(consumer_ref.kong_id).count()
        self.assertEqual(amount, 0)

        # Create auth
        auth_ref = OAuth2ReferenceFactory(consumer=consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Reload
        auth_ref = models.OAuth2Reference.objects.get(id=auth_ref.id)
        self.assertIsNotNone(auth_ref.kong_id)

        # Check kong
        result = self.client.consumers.oauth2(consumer_ref.kong_id).retrieve(auth_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['client_id'], auth_ref.client_id)

    def test_sync_consumer_multiple_oauth2(self):
        amount = 3

        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Create auths
        auths = []
        for i in range(amount):
            auths.append(OAuth2ReferenceFactory(consumer=consumer_ref))

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check
        self.assertEqual(self.client.consumers.oauth2(consumer_ref.kong_id).count(), amount)

        # Reload
        for i in range(len(auths)):
            auths[i] = models.OAuth2Reference.objects.get(id=auths[i].id)
            self.assertIsNotNone(auths[i].kong_id)

        # Check kong
        result = self.client.consumers.oauth2(consumer_ref.kong_id).list()
        self.assertIsNotNone(result)
        self.assertEqual(
            sorted([(uuid.UUID(r['id']), r['client_id']) for r in result['data']], key=lambda x: x[0]),
            sorted([(obj.kong_id, obj.client_id) for obj in auths], key=lambda x: x[0]))

    def test_withdraw_consumer_oauth2(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Create auth
        auth_ref = OAuth2ReferenceFactory(consumer=consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Reload
        auth_ref = models.OAuth2Reference.objects.get(id=auth_ref.id)
        self.assertIsNotNone(auth_ref.kong_id)
        self.assertTrue(auth_ref.synchronized)

        # Withdraw
        logic.withdraw_consumer(self.client, consumer_ref)
        self.assertFalse(consumer_ref.synchronized)

        # Reload
        auth_ref = models.OAuth2Reference.objects.get(id=auth_ref.id)
        self.assertIsNone(auth_ref.kong_id)
        self.assertFalse(auth_ref.synchronized)

    def test_delete_consumer_oauth2(self):
        # Create consumer_ref
        consumer_ref = ConsumerReferenceFactory(username=fake.consumer_name())

        # Create auth
        auth_ref1 = OAuth2ReferenceFactory(consumer=consumer_ref)
        OAuth2ReferenceFactory(consumer=consumer_ref)

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check
        self.assertEqual(self.client.consumers.oauth2(consumer_ref.kong_id).count(), 2)

        # Delete auth_ref1
        auth_ref1.delete()

        # Publish
        logic.synchronize_consumer(self.client, consumer_ref)
        self.assertTrue(consumer_ref.synchronized)

        # Check
        self.assertEqual(self.client.consumers.oauth2(consumer_ref.kong_id).count(), 1)

        # Delete consumer
        consumer_kong_id = consumer_ref.kong_id
        consumer_ref.delete()

        # Check
        with self.assertRaises(ValueError):
            self.client.consumers.oauth2(consumer_kong_id).count()

    def _cleanup_afterwards(self, consumer_ref):
        self._cleanup_consumers.append(consumer_ref)
        return consumer_ref


class AuthenticationPluginTestCase(TestCase):
    def setUp(self):
        self.client = get_kong_client()
        self._cleanup_api = []

    def tearDown(self):
        self.client.close()

        for api_ref in self._cleanup_api:
            self.assertTrue(isinstance(api_ref, models.APIReference))
            api_ref = models.APIReference.objects.get(id=api_ref.id)  # reloads!!
            logic.withdraw_api(self.client, api_ref)

    def test_create_oauth2_plugin(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Create plugin_configuration_ref
        plugin_configuration_ref = PluginConfigurationReferenceFactory(
            api=api_ref, plugin=Plugins.OAUTH2_AUTHENTICATION, config={})

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Reload plugin configuration
        plugin_configuration_ref = PluginConfigurationReference.objects.get(id=plugin_configuration_ref.id)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], Plugins.label(plugin_configuration_ref.plugin))

    def test_create_oauth2_plugin_with_scopes(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Create plugin_configuration_ref
        plugin_configuration_ref = PluginConfigurationReferenceFactory(
            api=api_ref, plugin=Plugins.OAUTH2_AUTHENTICATION, config={
                'scopes': 'email,subscriptions,topups'
            })

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Reload plugin configuration
        plugin_configuration_ref = PluginConfigurationReference.objects.get(id=plugin_configuration_ref.id)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertEqual(result['name'], Plugins.label(plugin_configuration_ref.plugin))
        self.assertEqual(result['config']['scopes'], ['email', 'subscriptions', 'topups'])

    def test_update_oauth2_plugin_with_scopes(self):
        # Create api_ref
        api_ref = APIReferenceFactory(upstream_url=fake.url(), request_host=fake.domain_name())

        # Create plugin_configuration_ref
        plugin_configuration_ref = PluginConfigurationReferenceFactory(
            api=api_ref, plugin=Plugins.OAUTH2_AUTHENTICATION, config={})

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Reload plugin configuration
        plugin_configuration_ref = PluginConfigurationReference.objects.get(id=plugin_configuration_ref.id)

        # Update plugin_configuration_ref
        plugin_configuration_ref.config = dict({
            'scopes': 'email,subscriptions,topups'
        }, **plugin_configuration_ref.config)
        plugin_configuration_ref.save()

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Reload plugin configuration
        plugin_configuration_ref = PluginConfigurationReference.objects.get(id=plugin_configuration_ref.id)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertEqual(result['config']['scopes'], ['email', 'subscriptions', 'topups'])

    def _cleanup_afterwards(self, api_ref):
        self._cleanup_api.append(api_ref)
        return api_ref
