# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import json
import six
from django_ace.widgets import AceWidget


class JSONWidget(AceWidget):
    def render(self, name, value, attrs=None):
        if not isinstance(value, six.string_types):
            value = json.dumps(value, sort_keys=True, indent=4, separators=(',', ': '))
        return super(JSONWidget, self).render(name, value, attrs)
