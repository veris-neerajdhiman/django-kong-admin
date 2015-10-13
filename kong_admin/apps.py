# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.apps import AppConfig


class KongAdminConfig(AppConfig):
    name = 'kong_admin'
    verbose_name = 'Kong'

    def ready(self):
        # See: http://stackoverflow.com/a/22924754/591217
        from kong_admin import receivers
