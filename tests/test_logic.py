from __future__ import unicode_literals, print_function

from django.test import TestCase

from kong_admin import models
from kong_admin.factory import get_kong_client
from kong_admin import logic

from .factories import APIReferenceFactory, PluginConfigurationReferenceFactory, PluginConfigurationFieldFactory, \
    ConsumerReferenceFactory
from .fake import fake


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
        api_ref = APIReferenceFactory(target_url=fake.url())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Try to sync, expect an error
        with self.assertRaises(ValueError):
            logic.synchronize_api(self.client, api_ref)

        self.assertFalse(api_ref.synchronized)

        # Fix api_ref
        api_ref.public_dns = fake.domain_name()
        api_ref.save()

        # Sync again
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)

    def test_sync_api(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Sync
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)

    def test_sync_updated_api(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)
        self.assertEqual(result['name'], api_ref.public_dns)

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
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)
        self.assertEqual(result['name'], new_name)

    def test_withdraw_api(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)

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
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)

        # You can delete afterwards
        api_kong_id = api_ref.kong_id
        api_ref.delete()

        # Check kong
        with self.assertRaises(ValueError):
            _ = self.client.apis.retrieve(api_kong_id)

    def test_sync_plugin_configuration_before_api(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Attempt to publish
        with self.assertRaises(ValueError):
            logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

    def test_sync_plugin_configuration_without_fields(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Check
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Attempt to publish
        with self.assertRaises(ValueError):
            logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

    def test_sync_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Check
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Create plugin_configuration field
        PluginConfigurationFieldFactory(configuration=plugin_configuration_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], plugin_configuration_ref.name)

    def test_withdraw_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Create plugin_configuration field
        PluginConfigurationFieldFactory(configuration=plugin_configuration_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], plugin_configuration_ref.name)

        # Withdraw plugin_configuration
        logic.withdraw_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        with self.assertRaises(ValueError):
            _ = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)

    def test_delete_synchronized_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Create plugin_configuration field
        PluginConfigurationFieldFactory(configuration=plugin_configuration_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], plugin_configuration_ref.name)

        # Delete plugin_configuration
        plugin_configuration_kong_id = plugin_configuration_ref.kong_id
        plugin_configuration_ref.delete()

        # Check
        with self.assertRaises(ValueError):
            _ = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_kong_id)

    def test_disable_synchronized_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Create plugin_configuration field
        PluginConfigurationFieldFactory(configuration=plugin_configuration_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], plugin_configuration_ref.name)
        self.assertTrue(result['enabled'])

        # Update plugin_configuration
        logic.enable_plugin_configuration(self.client, plugin_configuration_ref, enabled=False)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], plugin_configuration_ref.name)
        self.assertFalse(result['enabled'])

    def test_update_synchronized_plugin_configuration(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish api
        logic.synchronize_api(self.client, api_ref)

        # Create plugin_configuration
        plugin_configuration_ref = PluginConfigurationReferenceFactory(api=api_ref)

        # Create plugin_configuration field
        plugin_configuration_field = PluginConfigurationFieldFactory(configuration=plugin_configuration_ref)

        # Publish plugin_configuration
        logic.synchronize_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], plugin_configuration_ref.name)
        self.assertEqual(result['value'][plugin_configuration_field.property], plugin_configuration_field.value)

        # Update plugin_configuration
        new_value = 5
        self.assertNotEqual(new_value, plugin_configuration_field.value)
        plugin_configuration_field.value = new_value
        plugin_configuration_field.save()
        logic.publish_plugin_configuration(self.client, plugin_configuration_ref)

        # Check
        result = self.client.apis.plugins(api_ref.kong_id).retrieve(plugin_configuration_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], plugin_configuration_ref.name)
        self.assertEqual(result['value'][plugin_configuration_field.property], new_value)

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
        # Create incomplete api_ref
        consumer_ref = ConsumerReferenceFactory()

        # Mark for auto cleanup
        self._cleanup_afterwards(consumer_ref)

        # Try to sync, expect an error
        with self.assertRaises(ValueError):
            logic.synchronize_consumer(self.client, consumer_ref)

        self.assertFalse(consumer_ref.synchronized)

        # Fix api_ref
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
        # Create api_ref
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
        # Create api_ref
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
        # Create api_ref
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
        # Create api_ref
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

    def _cleanup_afterwards(self, consumer_ref):
        self._cleanup_consumers.append(consumer_ref)
        return consumer_ref
