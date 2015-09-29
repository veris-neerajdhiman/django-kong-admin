# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.utils.translation import ugettext_lazy as _
from django.core import validators as django_validators


name_validator = django_validators.RegexValidator(
    r'^[\w.~-]+$', _('Enter a valid username. This value may contain only letters, '
                     'numbers and ~/./-/_ characters.'), 'invalid')
