# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.apps import AppConfig
from kong_admin.receivers import *


class KongAdminConfig(AppConfig):
    name = 'kong_admin'
    verbose_name = 'Kong'

    # def ready(self):
    #     # WTF: What is the purpose of this? Shouldn't this deserve a bit of explanation?
    #     from kong_admin.receivers import __all__
