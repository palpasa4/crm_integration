from typing import Literal
from fastapi import APIRouter, Request
from src.api.dependencies import AnnotatedPluginManager, AnnotatedSettings
from src.core.exceptions import *
from src.api.handlers import valid_token


router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/authorization-url")
def get_authorization_url_resource(
    pm: AnnotatedPluginManager,
    settings: AnnotatedSettings,
    name: Literal["copper", "capsule", "hubspot", "zoho", "nimble"] | None = None,
):
    if not name:
        plugins =  pm.hook.get_auth_url(settings=settings)
        return dict(plugins)
    else:
        # Is there any other solution besides this??
        for impl in pm.hook.get_auth_url.get_hookimpls():
            plugin = impl.plugin
            if getattr(plugin, "name", None) == name:
                return impl.function(settings=settings)
        raise CRMNotFoundException(
            message=f"No plugin found for integration name '{name}'", status_code=404
        )


@router.get("/import-contacts")
def get_contacts_resource(
    settings: AnnotatedSettings,
    pm: AnnotatedPluginManager,
    name: Literal["copper", "capsule", "hubspot", "zoho", "nimble"] | None = None,
):
    if not name:
        pm.hook.get_contacts(settings=settings, pm=pm)
        return {"message": "Contacts imported and saved successfully for all CRMs!"}
    else:
        for impl in pm.hook.get_contacts.get_hookimpls():
            plugin = impl.plugin
            if getattr(plugin, "name", None) == name:
                impl.function(settings=settings, pm=pm)
                return {
                    "message": f"Contacts imported and saved successfully for CRM {name}!!"
                }
        raise CRMNotFoundException(
            message=f"No plugin found for integration name '{name}'", status_code=404
        )


@router.get("/export-contacts")
def create_contacts_resource(
    settings: AnnotatedSettings,
    pm: AnnotatedPluginManager,
    name: Literal["copper","capsule","hubspot","zoho","nimble"] | None = None
):
    if not name:
        pm.hook.create_contacts(settings=settings, pm=pm)
    else:
        for impl in pm.hook.create_contacts.get_hookimpls():
            plugin = impl.plugin
            if getattr(plugin, "name", None) == name:
                impl.function(settings=settings, pm= pm)
                return {"message": "Successfuly exported!"}
        raise CRMNotFoundException(
            message=f"No plugin found for CRM {name}", status_code=404
        )


@router.get("/revoke-token")
def revoke_token(pm: AnnotatedPluginManager):
    pm.hook.revoke_token()
    return {"message": "Token destroyed successfully!"}
