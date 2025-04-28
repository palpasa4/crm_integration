import pluggy, requests
from urllib.parse import urlencode
from pluggy import PluginManager
from src.config.settings import AppSettings
from src.api.handlers import *
from src.core.exceptions import *


hookimpl = pluggy.HookimplMarker("crmintegration")


class HubspotPlugin:

    name = "hubspot" 

    @hookimpl
    def get_auth_url(self, settings: AppSettings):
        print("Hubspot plugin is called.")
        base_uri = f"https://app-na2.hubspot.com/oauth/authorize"
        state = generate_and_store_state("hubspot")
        params = {
            "client_id": settings.hubspot.client_id,
            "redirect_uri": "http://localhost:8000/callbacks/integrations/hubspot",
            "scope": "oauth crm.objects.contacts.read crm.objects.contacts.write",
            "state": state,
        }
        query_string = urlencode(params)
        full_uri = f"{base_uri}?{query_string}"
        return self.name,full_uri

    @hookimpl
    def get_access_token(self, code: str, settings: AppSettings):
        base_uri = "https://api.hubapi.com/oauth/v1/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        body = {
            "grant_type": "authorization_code",
            "client_id": settings.hubspot.client_id,
            "client_secret": settings.hubspot.client_secret,
            "redirect_uri": "http://localhost:8000/callbacks/integrations/hubspot",
            "code": code,
        }
        response = requests.post(base_uri, headers=headers, data=body)
        if response.status_code != 200:
            raise CRMTokenException(
                message=response.text, status_code=response.status_code
            )
        save_token_with_expiry(self.name, response.json())

    @hookimpl
    def get_contacts(self, settings: AppSettings, pm: PluginManager):
        if not valid_token(self.name):
            pm.hook.get_new_token(settings=settings)
        base_uri = "https://api.hubapi.com/crm/v3/objects/contacts"
        access_token = get_value_from_json(
            "src/crmdata/token.json", self.name, "access_token"
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(base_uri, headers=headers)
        # response.raise_for_status()
        if response.status_code == 200:
            save_contacts(self.name, response.json())
        else:
            raise ImportContactsException(
                message=response.text, status_code=response.status_code
            )

    @hookimpl
    def create_contacts(self, settings: AppSettings, pm: PluginManager):
        if not valid_token(self.name):
            pm.hook.get_new_token(settings=settings)
        token = get_value_from_json("src/crmdata/token.json", self.name, "access_token")
        base_uri = "https://api.hubapi.com/crm/v3/objects/contacts"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "properties": {
                "email": "example@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "phone": "+123456789",
                "company": "Example Company"
            }
        }
        response = requests.post(base_uri, headers=headers, json=data)
        if response.status_code == 201:
            raise ContactExistsException(message="",status_code=response.status_code)

    @hookimpl
    def get_new_token(self, settings: AppSettings):
        base_uri = "https://api.hubapi.com/oauth/v1/token"
        refresh_token = get_value_from_json(
            "src/crmdata/token.json", self.name, "refresh_token"
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        body = {
            "grant_type": "refresh_token",
            "client_id": settings.hubspot.client_id,
            "client_secret": settings.hubspot.client_secret,
            "refresh_token": refresh_token,
        }
        response = requests.get(base_uri, headers=headers, data=body)
        response = requests.post(base_uri, data=body)
        if response.status_code == 200:
            save_token_with_expiry(self.name, response.json())
        else:
            raise CRMTokenException(
                message=response.text, status_code=response.status_code
            )
