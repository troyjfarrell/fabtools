"""
System settings
===============
"""
from __future__ import with_statement

from re import escape

from fabric.api import warn, shell_env
from fabric.contrib.files import append, uncomment

from fabtools.files import is_file, watch
from fabtools.system import (
    distrib_family, distrib_id,
    get_hostname, set_hostname,
    get_sysctl, set_sysctl,
    supported_locales,
)
from fabtools.utils import run_as_root


def sysctl(key, value, persist=True):
    """
    Require a kernel parameter to have a specific value.
    """
    if get_sysctl(key) != value:
        set_sysctl(key, value)

    if persist:

        from fabtools.require import file as require_file

        filename = '/etc/sysctl.d/60-%s.conf' % key
        with watch(filename, use_sudo=True) as config:
            require_file(filename,
                         contents='%(key)s = %(value)s\n' % locals(),
                         use_sudo=True)
        if config.changed:
            if distrib_family() == 'debian':
                run_as_root('service procps start')


def hostname(name):
    """
    Require the hostname to have a specific value.
    """
    if get_hostname() != name:
        set_hostname(name)


def locales(names):
    """
    Require the list of locales to be available.
    """

    config_file = '/var/lib/locales/supported.d/local'

    if not is_file(config_file):
        config_file = '/etc/locale.gen'

    # Regenerate locales if config file changes
    with watch(config_file, use_sudo=True) as config:

        # Add valid locale names to the config file
        supported = dict(supported_locales())
        for name in names:
            if name in supported:
                charset = supported[name]
                locale = "%s %s" % (name, charset)
                with shell_env():
                    uncomment(config_file, escape(locale), use_sudo=True)
                    append(config_file, locale, use_sudo=True, partial=True)
            else:
                warn('Unsupported locale name "%s"' % name)

    if config.changed:
        if distrib_id() == "Archlinux":
            run_as_root('locale-gen')
        else:
            run_as_root('dpkg-reconfigure --frontend=noninteractive locales')


def locale(name):
    """
    Require the locale to be available.
    """
    locales([name])


def default_locale(name):
    """
    Require the locale to be the default.
    """
    from fabtools.require import file as require_file

    # Ensure the locale is available
    locale(name)

    # Make it the default
    contents = 'LANG="%s"\n' % name
    if distrib_id() == "Archlinux":
        config_file = '/etc/locale.conf'
    else:
        config_file = '/etc/default/locale'
    require_file(config_file, contents, use_sudo=True)
