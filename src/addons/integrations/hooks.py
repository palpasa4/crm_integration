import pluggy
from fastapi import Request
from src.config.settings import AppSettings


hookspec = pluggy.HookspecMarker("crmintegration")


class Spec:
    @hookspec
    def get_auth_url(self, settings: AppSettings): ...

    @hookspec
    def get_access_token(self, code: str, settings: AppSettings): ...

    @hookspec
    def get_contacts(self, settings: AppSettings, pm: pluggy.PluginManager): ...

    @hookspec
    def create_contacts(self, settings: AppSettings, pm: pluggy.PluginManager): ...

    @hookspec
    def get_new_token(self, settings: AppSettings): ...

    @hookspec
    def revoke_token(self): ...
