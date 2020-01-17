# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import resourcemanager.ap


class ResourcemanagerApLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=resourcemanager.ap)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'resourcemanager.ap:default')


RESOURCEMANAGER_AP_FIXTURE = ResourcemanagerApLayer()


RESOURCEMANAGER_AP_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RESOURCEMANAGER_AP_FIXTURE,),
    name='ResourcemanagerApLayer:IntegrationTesting',
)


RESOURCEMANAGER_AP_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RESOURCEMANAGER_AP_FIXTURE,),
    name='ResourcemanagerApLayer:FunctionalTesting',
)


RESOURCEMANAGER_AP_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        RESOURCEMANAGER_AP_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='ResourcemanagerApLayer:AcceptanceTesting',
)
