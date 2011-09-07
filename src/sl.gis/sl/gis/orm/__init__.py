from sl.geodialogues import config

from zope.i18nmessageid import MessageFactory

from Products.Archetypes import atapi
from Products.CMFCore import utils

from Products.CMFCore.utils import ToolInit

# the message factory
slMessageFactory = MessageFactory('sl.gis')

packageName = __name__

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    pass