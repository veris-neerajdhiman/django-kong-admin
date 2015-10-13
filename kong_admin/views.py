# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from contextlib import closing
import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import HttpResponse

from . import logic, factory
from .models import APIReference, ConsumerReference


@staff_member_required
def synchronize_api_references(request, queryset=None):
    return _synchronize_multiple_references(request, logic.synchronize_apis, 'API', queryset=queryset)


@staff_member_required
def synchronize_api_reference(request, pk, toggle_enable=False):
    obj = APIReference.objects.get(id=pk)
    return _synchronize_single_reference(request, logic.synchronize_api, 'API', obj, toggle_enable=toggle_enable)


@staff_member_required
def synchronize_consumer_references(request, queryset=None):
    return _synchronize_multiple_references(request, logic.synchronize_consumers, 'Consumer', queryset=queryset)


@staff_member_required
def synchronize_consumer_reference(request, pk, toggle_enable=False):
    obj = ConsumerReference.objects.get(id=pk)
    return _synchronize_single_reference(
        request, logic.synchronize_consumer, 'Consumer', obj, toggle_enable=toggle_enable)


@staff_member_required
def show_config(request):
    """
    This view shows the configuration as it is known by Kong
    """
    if not request.user.is_staff:
        return HttpResponse('Only staff is authorized to view the configuration', status=403)

    kong = factory.get_kong_client()

    result = {
        'apis': list(kong.apis.iterate()),
        'consumers': list(kong.consumers.iterate()),
    }

    for i in range(len(result['apis'])):
        result['apis'][i]['plugins'] = list(kong.apis.plugins(result['apis'][i]['id']).iterate()),

    for i in range(len(result['consumers'])):
        result['consumers'][i]['basicauth'] = list(kong.consumers.basic_auth(result['consumers'][i]['id']).iterate()),
        result['consumers'][i]['keyauth'] = list(kong.consumers.key_auth(result['consumers'][i]['id']).iterate()),
        result['consumers'][i]['oauth2'] = list(kong.consumers.oauth2(result['consumers'][i]['id']).iterate()),

    config = json.dumps(result, sort_keys=True, indent=4, separators=(', ', ': '))
    return render(request, 'kong_admin/show_config.html', {'config': config})


def _synchronize_multiple_references(request, sync_func, entity_name, queryset=None):
    try:
        with closing(factory.get_kong_client()) as client:
            queryset = sync_func(client, queryset=queryset)
    except Exception as e:
        messages.add_message(
            request, messages.ERROR, 'Could not synchronize %s References: %s' % (entity_name, str(e)))
    else:
        messages.add_message(
            request, messages.SUCCESS, 'Successfully synchronized %d %s References (it can take a while before the '
                                       'changes are visible!)' % (queryset.count(), entity_name))
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def _synchronize_single_reference(request, sync_func, entity_name, obj, toggle_enable=False):
    try:
        with closing(factory.get_kong_client()) as client:
            sync_func(client, obj, toggle=toggle_enable)
    except Exception as e:
        messages.add_message(
            request, messages.ERROR, 'Could not sync %s Reference: %s (was it published?)' % (entity_name, str(e)))
    else:
        messages.add_message(
            request, messages.SUCCESS, 'Successfully synced %s Reference (it can take a while before the '
                                       'changes are visible!)' % entity_name)

    return HttpResponseRedirect(request.META["HTTP_REFERER"])
