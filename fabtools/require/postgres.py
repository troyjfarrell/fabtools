"""
PostgreSQL users and databases
==============================
"""
from __future__ import with_statement

from fabric.api import cd, hide, run, settings
from fabtools.files import is_file, watch
from fabtools.postgres import (
    create_database,
    create_user,
    database_exists,
    user_exists,
)
from fabtools.require.deb import package
from fabtools.require.service import started, restarted
from fabtools.require.system import locale as require_locale


def _service_name(version=None):

    if is_file('/etc/init.d/postgresql'):
        return 'postgresql'

    if version and is_file('/etc/init.d/postgresql-%s' % version):
        return 'postgresql-%s' % version

    with cd('/etc/init.d'):
        with settings(hide('running', 'stdout')):
            return run('ls postgresql-*').splitlines()[0]


def server(version=None):
    """
    Require a PostgreSQL server to be installed and running.

    ::

        from fabtools import require

        require.postgres.server()

    """
    if version:
        pkg_name = 'postgresql-%s' % version
    else:
        pkg_name = 'postgresql'
    package(pkg_name)

    started(_service_name(version))


def user(name, password, superuser=False, createdb=False,
         createrole=False, inherit=True, login=True, connection_limit=None,
         encrypted_password=False):
    """
    Require the existence of a PostgreSQL user. The password and options
    provided will only be applied when creating a new user (existing
    users will *not* be modified).

    ::

        from fabtools import require

        require.postgres.user('dbuser', password='somerandomstring')

        require.postgres.user('dbuser2', password='s3cr3t',
            createdb=True, create_role=True, connection_limit=20)

    """
    if not user_exists(name):
        create_user(name, password, superuser, createdb, createrole, inherit,
                    login, connection_limit, encrypted_password)


def database(name, owner, template='template0', encoding='UTF8',
             locale='en_US.UTF-8'):
    """
    Require a PostgreSQL database.

    ::

        from fabtools import require

        require.postgres.database('myapp', owner='dbuser')

    """
    if not database_exists(name):

        with watch('/etc/locale.gen') as locales:
            require_locale(locale)
        if locales.changed:
            restarted(_service_name())

        create_database(name, owner, template=template, encoding=encoding,
                        locale=locale)
