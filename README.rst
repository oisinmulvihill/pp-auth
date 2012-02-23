pp-auth
=======

.. contents::


Introduction
------------

This module provides the low level user, group and other tables which can be
interface to with Repoze.who and Repoze.what. It is the intention that our
Pyramid / wsgi web projects use pp-auth and Repoze in a common way. I.e. tnav
and bookingsys.

This provides the namespaced package: pp.auth


Testing
-------

Activate the dev environment and change into pp-auth.


Run all tests
~~~~~~~~~~~~~

From here you can do::

    python runtests.py -s


