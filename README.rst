=================
django-kong-admin
=================

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |circleci| |coveralls| |scrutinizer|
    * - package
      - |version| |downloads| |wheel|
    * - compatibility
      - |pyversions| |implementation|

.. |docs| image:: https://readthedocs.org/projects/django-kong-admin/badge/?style=flat
    :target: https://readthedocs.org/projects/django-kong-admin
    :alt: Documentation Status

.. |circleci| image:: https://img.shields.io/circleci/project/vikingco/django-kong-admin.svg?style=flat&label=CircleCI
    :alt: CircleCI Build Status
    :target: https://circleci.com/gh/vikingco/django-kong-admin

.. |coveralls| image:: http://img.shields.io/coveralls/vikingco/django-kong-admin/master.svg?style=flat&label=Coveralls
    :alt: Coverage Status
    :target: https://coveralls.io/github/vikingco/django-kong-admin

.. |version| image:: http://img.shields.io/pypi/v/django-kong-admin.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/django-kong-admin

.. |downloads| image:: http://img.shields.io/pypi/dm/django-kong-admin.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/django-kong-admin

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/vikingco/django-kong-admin/master.svg?style=flat
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/vikingco/django-kong-admin/

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/django-kong-admin.svg?style=flat
    :alt: Supported python versions
    :target: https://pypi.python.org/pypi/django-kong-admin

.. |implementation| image:: https://img.shields.io/pypi/implementation/django-kong-admin.svg?style=flat
    :alt: Supported imlementations
    :target: https://pypi.python.org/pypi/django-kong-admin

.. |wheel| image:: https://img.shields.io/pypi/wheel/django-kong-admin.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/django-kong-admin

A reusable Django App to manage a Kong service (https://getkong.org)

=== HOWTO ===

.. code:: bash

    pip install django-kong-admin

In your Django Settings:

.. code:: python

    INSTALLED_APPS = (
        ....
        'jsonfield2',  # Used in the models - https://github.com/DarioGT/django-jsonfield2
        'django_ace',  # Used in the 'show_config' view - https://github.com/bradleyayers/django-ace
        'kong_admin'
        ....
    )

    # Tweak to your own needs
    KONG_ADMIN_URL = 'http://localhost:8001'
    KONG_ADMIN_SIMULATOR = False  # python-kong includes a simulator for testing purposes. You usually don't need that.

In your base url patterns:

.. code:: python

    urlpatterns = [
        ....
        url(r'^admin/', include(admin.site.urls)),
        ....
        # Optionally, add the following url, which is a view that displays the current kong config:
        url(r'^showconfig/', 'kong_admin.views.show_config')
        .... 
    ]

Run default Django management commands to get things working

.. code:: bash

    python manage.py migrate
    python manage.py collectstatic
    ...

Then you can go to your Django admin site, and the Kong Admin entities
will be manageable.

I plan to add more documentation in the near future! If you want to
contribute to the library, be my guest!
