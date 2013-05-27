"""
Git
===

This module provides high-level tools for managing `Git`_ repositories.

.. _Git: http://git-scm.com/

"""

from __future__ import with_statement

from fabric.api import run

from fabtools import git
from fabtools.files import is_dir


def command():
    """
    Require the git command-line tool.

    Example::

        from fabric.api import run
        from fabtools import require

        require.git.command()
        run('git --help')

    """
    from fabtools.require.deb import package as require_deb_package
    from fabtools.require.rpm import package as require_rpm_package
    from fabtools.system import distrib_family

    res = run('git --version', quiet=True)
    if res.failed:
        family = distrib_family()
        if family == 'debian':
            require_deb_package('git-core')
        elif family == 'redhat':
            require_rpm_package('git')
        else:
            raise NotImplementedError()


def working_copy(remote_url, path=None, branch="master", update=True,
                 use_sudo=False, user=None):
    """
    Require a working copy of the repository from the ``remote_url``.

    The ``path`` is optional, and defaults to the last segment of the
    remote repository URL, without its ``.git`` suffix.

    If the ``path`` does not exist, this will clone the remote
    repository and check out the specified branch.

    If the ``path`` exists and ``update`` is ``True``, it will fetch
    changes from the remote repository, check out the specified branch,
    then merge the remote changes into the working copy.

    If the ``path`` exists and ``update`` is ``False``, it will only
    check out the specified branch, without fetching remote changesets.

    :param remote_url: URL of the remote repository (e.g.
                       https://github.com/ronnix/fabtools.git).  The given URL
                       will be the ``origin`` remote of the working copy.
    :type remote_url: str

    :param path: Absolute or relative path of the working copy on the
                 filesystem.  If this directory doesn't exist yet, a new
                 working copy is created through ``git clone``.  If the
                 directory does exist *and* ``update == True``, a
                 ``git fetch`` is issued.  If ``path is None`` the
                 ``git clone`` is issued in the current working directory and
                 the directory name of the working copy is created by ``git``.
    :type path: str

    :param branch: Branch to check out.
    :type branch: str

    :param update: Whether or not to fetch and merge remote changesets.
    :type update: bool

    :param use_sudo: If ``True`` execute ``git`` with
                     :func:`fabric.operations.sudo`, else with
                     :func:`fabric.operations.run`.
    :type use_sudo: bool

    :param user: If ``use_sudo is True``, run :func:`fabric.operations.sudo`
                 with the given user.  If ``use_sudo is False`` this parameter
                 has no effect.
    :type user: str
    """

    command()

    if path is None:
        path = remote_url.split('/')[-1].rstrip('.git')

    if is_dir(path, use_sudo=use_sudo) and update:
        git.fetch(path=path, use_sudo=use_sudo, user=user)
        git.checkout(path=path, branch=branch, use_sudo=use_sudo, user=user)
        git.pull(path=path, use_sudo=use_sudo, user=user)

    elif is_dir(path, use_sudo=use_sudo) and not update:
        git.checkout(path=path, branch=branch, use_sudo=use_sudo, user=user)

    elif not is_dir(path, use_sudo=use_sudo):
        git.clone(remote_url, path=path, use_sudo=use_sudo, user=user)
        git.checkout(path=path, branch=branch, use_sudo=use_sudo, user=user)

    else:
        raise ValueError("Invalid combination of parameters.")
