from contextlib import asynccontextmanager
from src.api.entrypoints import routes, callbacks
from fastapi import FastAPI
from src.config.settings import AppSettings
from src.addons.integrations.plugin_manager import create_plugin_manager
from src.core.middleware import CustomExceptionMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    app.state.settings = AppSettings()
    app.state.plugin_manager = create_plugin_manager()
    yield
    print("Shutting down...")


def init_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(CustomExceptionMiddleware)
    app.include_router(routes.router)
    app.include_router(callbacks.router)
    return app


app = init_app()
