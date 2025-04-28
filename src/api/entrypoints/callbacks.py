from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIWebSocketRoute
from src.addons.integrations.plugins import hubspot
from src.api.dependencies import AnnotatedPluginManager, AnnotatedSettings
from src.api.handlers import check_state
from src.core.exceptions import *


router = APIRouter(prefix="/callbacks", tags=["Callbacks"])


@router.get("/integrations/{name}")
def generate_access_token(
    name: str,
    code: str,
    
    state: str,
    pm: AnnotatedPluginManager,
    settings: AnnotatedSettings,
):
    check_state(name, state)
    for impl in pm.hook.get_access_token.get_hookimpls():
        plugin = impl.plugin
        if getattr(plugin, "name", None) == name:
            impl.function(code=code, settings=settings)
            return {
                "message": f"Token saved successfully. You can import contacts now for integration name: {name}!"
            }
    raise CRMNotFoundException(
        message=f"No plugin found for integration name '{name}'", status_code=404
    )
