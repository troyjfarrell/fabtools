.. image:: https://api.travis-ci.org/ronnix/fabtools.png
    :target: http://travis-ci.org/ronnix/fabtools

About
=====

``fabtools`` includes useful functions to help you write your `Fabric <http://fabfile.org/>`_ files.

``fabtools`` makes it easier to manage system users, packages, databases, etc.

``fabtools`` includes a number of low-level actions, as well as a higher level interface called ``fabtools.require``.

Using ``fabtools.require`` allows you to use a more declarative style, similar to Chef or Puppet.

Installing
==========

To install the latest release from `PyPI <http://pypi.python.org/pypi/fabtools>`_

.. code-block:: console

    $ pip install fabtools

To install the latest development version from `GitHub <https://github.com/ronnix/fabtools>`_

.. code-block:: console

    $ pip install git+git://github.com/ronnix/fabtools.git

Example
=======

Here is an example ``fabfile.py`` using ``fabtools``

.. code-block:: python

    from fabric.api import *
    from fabtools import require
    import fabtools

    @task
    def setup():

        # Require some Debian/Ubuntu packages
        require.deb.packages([
            'imagemagick',
            'libxml2-dev',
        ])

        # Require a Python package
        with fabtools.python.virtualenv('/home/myuser/env'):
            require.python.package('pyramid')

        # Require an email server
        require.postfix.server('example.com')

        # Require a PostgreSQL server
        require.postgres.server()
        require.postgres.user('myuser', 's3cr3tp4ssw0rd')
        require.postgres.database('myappsdb', 'myuser')

        # Require a supervisor process for our app
        require.supervisor.process('myapp',
            command='/home/myuser/env/bin/gunicorn_paster /home/myuser/env/myapp/production.ini',
            directory='/home/myuser/env/myapp',
            user='myuser'
            )

        # Require an nginx server proxying to our app
        require.nginx.proxied_site('example.com',
            docroot='/home/myuser/env/myapp/myapp/public',
            proxy_url='http://127.0.0.1:8888'
            )

        # Setup a daily cron task
        fabtools.cron.add_daily('maintenance', 'myuser', 'my_script.py')

Supported targets
=================

``fabtools`` currently supports the following target operating systems:

* Debian 6.0 (squeeze)

* Ubuntu 10.04 (lucid)
* Ubuntu 12.04 (precise)

* RHEL 5/6
* CentOS 5/6
* Scientific Linux 5/6

* SmartOS (Joyent)

* Archlinux

Contributions to help support other Unix/Linux distributions are welcome!
