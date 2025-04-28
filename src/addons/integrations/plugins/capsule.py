import pluggy, requests
from pluggy import HookimplOpts, PluginManager
from src.config.settings import AppSettings
from urllib.parse import urlencode
from fastapi import HTTPException, Request
from datetime import datetime
from src.core.exceptions import *
from src.api.handlers import *


hookimpl = pluggy.HookimplMarker("crmintegration")


class CapsulePlugin:

    name = "capsule"

    @hookimpl
    def get_auth_url(self, settings: AppSettings):
        print("Capsule plugin is called.")
        base_uri = "https://api.capsulecrm.com/oauth/authorise"
        state = generate_and_store_state("capsule")
        params = {
            "response_type": "code",
            "client_id": settings.capsule.client_id,
            "redirect_url": "http://localhost:8000/callbacks/integrations/capsule",
            "scope": "read write",
            "state": state,
        }
        query_string = urlencode(params)
        full_uri = f"{base_uri}?{query_string}"
        return self.name, full_uri

    @hookimpl
    def get_access_token(self, code: str, settings: AppSettings):
        base_uri = "https://api.capsulecrm.com/oauth/token"
        body = {
            "code": code,
            "client_id": settings.capsule.client_id,
            "client_secret": settings.capsule.client_secret,
            "grant_type": "authorization_code",
        }
        response = requests.post(base_uri, data=body)
        if response.status_code != 200:
            raise CRMTokenException(
                message=response.text, status_code=response.status_code
            )
        save_token_with_expiry(self.name, response.json())

    @hookimpl
    def get_contacts(self, settings: AppSettings, pm: PluginManager):
        if not valid_token(self.name):
            pm.hook.get_new_token(settings=settings)
        token = get_value_from_json("src/crmdata/token.json", self.name, "access_token")
        base_uri = "https://api.capsulecrm.com/api/v2/parties"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        response = requests.get(base_uri, headers=headers)
        if response.status_code == 200:
            save_contacts(self.name, response.json())
        else:
            raise ImportContactsException(
                message=response.text, status_code=response.status_code
            )


    @hookimpl
    def get_new_token(self, settings: AppSettings):
        base_uri = "https://api.capsulecrm.com/oauth/token"
        refresh_token = get_value_from_json(
            "src/crmdata/token.json", "capsule", "refresh_token"
        )
        body = {
            "client_id": settings.capsule.client_id,
            "client_secret": settings.capsule.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(base_uri, data=body)
        if response.status_code == 200:
            save_token_with_expiry(self.name, response.json())
        else:
            raise CRMTokenException(
                message=response.text, status_code=response.status_code
            )

    @hookimpl
    def revoke_token(self):
        refresh_token = get_value_from_json(
            "src/crmdata/token.json", "capsule", "refresh_token"
        )
        base_uri = "https://api.capsulecrm.com/oauth/token/revoke"
        body = {"token": refresh_token}
        response = requests.post(base_uri, data=body)

        if response.status_code == 200:
            clear_json("src/crmdata/token.json")
            clear_json("src/crmdata/state.json")
        else:
            raise CRMTokenException(
                message=response.text, status_code=response.status_code
            )
