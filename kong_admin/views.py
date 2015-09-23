# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http.response import HttpResponse

from .factory import get_kong_client


@login_required
def show_config(request):
    """
    Debug view, this should not be used in production!
    This view shows the configuration as it is known by Kong

    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponse('Only staff is authorized to view the configuration', status=403)

    kong = get_kong_client()

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

    config = json.dumps(result, sort_keys=True, indent=4, separators=(',', ': '))
    return render(request, 'kong_admin/show_config.html', {'config': config})
