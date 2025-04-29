from contextlib import asynccontextmanager
import httpx
from typing import Annotated
from fastapi import Depends, Request
from pluggy import PluginManager
from src.config.settings import AppSettings


def get_plugin_manager(request: Request) -> PluginManager:
    return request.app.state.plugin_manager


def get_app_settings(request: Request) -> AppSettings:
    return request.app.state.settings


AnnotatedPluginManager = Annotated[PluginManager, Depends(get_plugin_manager)]

AnnotatedSettings = Annotated[AppSettings, Depends(get_app_settings)]

