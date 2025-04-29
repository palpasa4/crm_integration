from typing import Literal, List
from fastapi import APIRouter, Query, Request
from src.api.dependencies import AnnotatedPluginManager, AnnotatedSettings
from src.core.exceptions import *
from src.api.handlers import valid_token


router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/authorization-url")
def get_authorization_url_resource(
    pm: AnnotatedPluginManager,
    settings: AnnotatedSettings,
    name: List[str] = Query(default=None),
):
    if not name:
        plugins = pm.hook.get_auth_url(settings=settings)
    else:
        matching_plugins = [
            impl.plugin
            for impl in pm.hook.get_auth_url.get_hookimpls()
            if getattr(impl.plugin, "name", None) in name
        ]
        if not matching_plugins:
            raise CRMNotFoundException(
                message=f"No plugins found for integration '{name}'", status_code=404
            )
        subset = pm.subset_hook_caller(
            "get_auth_url",
            remove_plugins=[
                plugin for plugin in pm.get_plugins() if plugin not in matching_plugins
            ]
        )
        plugins = subset(settings=settings)
    return dict(plugins)


@router.get("/import-contacts")
def get_contacts_resource(
    settings: AnnotatedSettings,
    pm: AnnotatedPluginManager,
    name: Literal["copper", "capsule", "hubspot", "zoho", "nimble"] | None = None,
):
    if not name:
        pm.hook.get_contacts(settings=settings)
        return {"message": "Contacts imported and saved successfully for all CRMs!"}
    else:
        for impl in pm.hook.get_contacts.get_hookimpls():
            plugin = impl.plugin
            if getattr(plugin, "name", None) == name:
                impl.function(settings=settings)
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
    name: Literal["copper", "capsule", "hubspot", "zoho", "nimble"] | None = None,
):
    if not name:
        pm.hook.create_contacts(settings=settings, pm=pm)
    else:
        for impl in pm.hook.create_contacts.get_hookimpls():
            plugin = impl.plugin
            if getattr(plugin, "name", None) == name:
                impl.function(settings=settings, pm=pm)
                return {"message": "Successfuly exported!"}
        raise CRMNotFoundException(
            message=f"No plugin found for CRM {name}", status_code=404
        )


@router.get("/revoke-token")
def revoke_token(pm: AnnotatedPluginManager):
    pm.hook.revoke_token()
    return {"message": "Token destroyed successfully!"}
