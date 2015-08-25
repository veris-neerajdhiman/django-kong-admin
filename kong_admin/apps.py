# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.apps import AppConfig


class KongAdminConfig(AppConfig):
    name = 'kong_admin'
    verbose_name = 'Kong'

    def ready(self):
        from kong_admin.receivers import __all__
