# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import copy
from django.conf.urls import url
from django.contrib.admin import ModelAdmin
from django.utils.safestring import mark_safe


class ActionButtonModelAdmin(ModelAdmin):
    change_list_template = 'kong_admin/action_button_admin_change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['buttons'] = getattr(self, 'action_buttons', [])
        return super(ActionButtonModelAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_action_buttons(self):
        return getattr(self, 'action_buttons', [])

    def get_list_display_buttons(self):
        return getattr(self, 'list_display_buttons', [])

    def get_urls(self):
        urls = super(ActionButtonModelAdmin, self).get_urls()
        action_buttons = self.get_action_buttons()
        list_display_buttons = self.get_list_display_buttons()

        custom_urls = []

        for button in action_buttons:
            custom_urls.append(url(r'^%s$' % button['url'], button['view']))

        for button in list_display_buttons:
            # Add pk attribute regex that will always be provided
            button_url = ActionButtonModelAdmin._safe_list_display_button_url(button['url']) + r'(?P<pk>\d+)/'
            custom_urls.append(url(r'^%s$' % button_url, button['view']))

        # my_urls = patterns("", *custom_urls)
        return custom_urls + urls

    def get_list_display(self, request):
        list_display_buttons = self.get_list_display_buttons()
        if not list_display_buttons:
            return self.list_display
        return self.list_display + (self._item_actions,)

    def _item_actions(self, obj):
        result = ''
        for button in self.get_list_display_buttons():
            result += ActionButtonModelAdmin._render_list_display_button(obj, button)
        return mark_safe(result)
    _item_actions.short_description = 'Item Actions'

    @staticmethod
    def _render_list_display_button(obj, button):
        button = copy.copy(button)
        for key in ('url', 'caption'):
            if callable(button[key]):
                button[key] = button[key](obj)

        # Add pk attribute that will always be provided
        button['url'] = '%s%d/' % (ActionButtonModelAdmin._safe_list_display_button_url(button['url']), obj.pk)

        # Return rendered button
        return mark_safe('<a href="%(url)s"><input type="button" value="%(caption)s" /></a>' % button)

    @staticmethod
    def _safe_list_display_button_url(button_url):
        if not button_url.endswith('/'):
            button_url += '/'
        return button_url
