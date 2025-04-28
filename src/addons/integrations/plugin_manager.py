import pluggy
from src.addons.integrations.hooks import Spec
from src.addons.integrations.plugins.hubspot import HubspotPlugin
from src.addons.integrations.plugins.capsule import CapsulePlugin


def create_plugin_manager() -> pluggy.PluginManager:
    pm = pluggy.PluginManager("crmintegration")
    pm.add_hookspecs(Spec)
    pm.register(CapsulePlugin(), name="capsule")
    pm.register(HubspotPlugin(), name="hubspot")
    return pm
