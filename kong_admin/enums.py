# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django_enumfield import enum


class Plugins(enum.Enum):
    SSL = 1
    KEY_AUTHENTICATION = 2
    BASIC_AUTHENTICATION = 3
    OAUTH2_AUTHENTICATION = 4
    RATE_LIMITING = 5
    TCP_LOG = 6
    UDP_LOG = 7
    FILE_LOG = 8
    HTTP_LOG = 9
    CORS = 10
    REQUEST_TRANSFORMER = 11
    REPONSE_TRANSFORMER = 12
    REQUEST_SIZE_LIMITING = 13

    labels = {
        SSL: 'ssl',
        KEY_AUTHENTICATION: 'key-authentication',
        BASIC_AUTHENTICATION: 'basic-authentication',
        OAUTH2_AUTHENTICATION: 'oauth2-authentication',
        RATE_LIMITING: 'rate-limiting',
        TCP_LOG: 'tcp-log',
        UDP_LOG: 'udp-log',
        FILE_LOG: 'file-log',
        HTTP_LOG: 'http-log',
        CORS: 'cors',
        REQUEST_TRANSFORMER: 'request-transformer',
        REPONSE_TRANSFORMER: 'response-transformer',
        REQUEST_SIZE_LIMITING: 'request-size-limiting'
    }
