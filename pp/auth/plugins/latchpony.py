# -*- coding: utf-8 -*-
"""
"""
import logging

from repoze.what.adapters import BaseSourceAdapter, SourceError

from pp.latchpony.client import rest


def get_log(extra=None):
    m = "{}.{}".format(__name__, extra) if extra else __name__
    return logging.getLogger(m)


def register():
    """
    """
    return {
        'authenticators': None,
        'mdproviders': None,
        'groups': get_groups_from_config,
        'permissions': get_permissions_from_config,
    }


class LatchPonyAdapter(BaseSourceAdapter):
    """Base class for LatchPony Group/Perm adapters."""

    def __init__(self, organisation, latchpony_service_uri):
        """
        :param org: An organisation identifier.

        :param latchpony_service_uri: http://<host>:<port>

        """
        super(LatchPonyAdapter, self).__init__()

        # for now, the adapter is read-only
        self.is_writable = False
        self._info = {}
        self.organisation = organisation
        self.uri = latchpony_service_uri
        self.lps = rest.LatchPonyService(self.uri)

    def info():
        """Reconnect/Retry a request to latchpony service.
        """
        doc = "Groups / Permission data."

        def fget(self):
            """Recover the Groups / Permission data.
            """
            from requests import ConnectionError

            try:
                # Check the service is running:
                #self.lps.ping()
                # self.log.debug(
                #     "latchpony: contacting '{:s}'.".format(self.uri)
                # )

                if self.__class__.__name__ == "LatchPonyGroupAdapter":
                    self._info = self.lps.groups_for(self.organisation)

                elif self.__class__.__name__ == "LatchPonyPermissionsAdapter":
                    self._info = self.lps.perms_for(self.organisation)

            except ConnectionError:
                self.log.exception(
                    "Cannot connect to latchpony: '{:s}' ".format(self.uri)
                )

            return self._info

        def fset(self, value):
            raise NotImplemented("Setting groups/perms directly.")

        def fdel(self):
            raise NotImplemented("Removing groups/perms directly.")

        return locals()

    info = property(**info())

    def _get_all_sections(self):
        return self.info

    def _get_section_items(self, section):
        return set(self.info[section])

    def _find_sections(self, hint):
        raise SourceError('This is implemented in the groups and '
                          'permissions adapters.')

    def _include_items(self, section, items):
        raise SourceError('For including items you must edit the '
                          'INI file directly.')

    def _item_is_included(self, section, item):
        return item in self.info[section]

    def _section_exists(self, section):
        return section in self.info


class LatchPonyGroupAdapter(LatchPonyAdapter):
    """Group Adapter."""

    log = get_log("LatchPonyGroupAdapter")

    def _find_sections(self, hint):
        userid = hint['repoze.who.userid']
        answer = set()
        for section in self.info.keys():
            if userid in self.info[section]:
                answer.add(section)
        return answer


class LatchPonyPermissionsAdapter(LatchPonyAdapter):
    """Permissions Adapters."""

    log = get_log("LatchPonyPermissionsAdapter")

    def _find_sections(self, hint):
        answer = set()
        for section in self.info.keys():
            if hint in self.info[section]:
                answer.add(section)
        return answer


def get_groups_from_config(settings, prefix="pp.auth.latchpony."):
    """Create an instance of LatchPonyPermissionsAdapter from configuration.
    """
    log = get_log("LatchPonyGroupAdapter")

    organisation = settings['%sorganisation' % prefix]
    uri = settings['%suri' % prefix]
    log.debug("organisation<%s> latchpony<%s>" % (organisation, uri))

    return LatchPonyGroupAdapter(organisation, uri)


def get_permissions_from_config(settings, prefix="pp.auth.latchpony."):
    """Create an instance of LatchPonyPermissionsAdapter from configuration.
    """
    log = get_log("get_groups_from_config")

    organisation = settings['%sorganisation' % prefix]
    uri = settings['%suri' % prefix]
    log.debug("organisation<%s> latchpony<%s>" % (organisation, uri))

    return LatchPonyPermissionsAdapter(organisation, uri)
