# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from unittest import TestCase
from django.core.exceptions import ValidationError

from kong_admin.validators import name_validator


class ValidatorTestCase(TestCase):
    def test_name_validator_only_letters(self):
        name_validator('Test')

    def test_name_validator_only_numbers(self):
        name_validator('123')

    def test_name_validator_letters_and_numbers(self):
        name_validator('Test123')

    def test_name_validator_include_legal_characters(self):
        legal_characters = '.~-_'

        for character in legal_characters:
            name_validator('Test%s123' % character)

    def test_name_validator_include_illegal_characters(self):
        illegal_characters = ' !@#$%^&*()+={}[]\\|"\'?/<>,'

        for character in illegal_characters:
            with self.assertRaises(ValidationError):
                name_validator('Test%s123' % character)
