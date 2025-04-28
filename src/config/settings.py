from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseIntegrationSettings(BaseModel):
    client_id: str
    client_secret: str


class CapsuleSettings(BaseIntegrationSettings): ...


class HubspotSettings(BaseIntegrationSettings): ...


class AppSettings(BaseSettings):
    capsule: CapsuleSettings
    hubspot: HubspotSettings

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
