from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from zope import schema
from zope.interface import Interface


class IAPKeys(Interface):

    api_key = schema.TextLine(
        title=u"Associated Press API Key",
        description=u"Key to access the API.",
    )


class APKeysEditForm(RegistryEditForm):
    """
    Define form logic
    """
    schema = IAPKeys
    label = u"Associated Press Keys"


class APKeysView(ControlPanelFormWrapper):
    form = APKeysEditForm
