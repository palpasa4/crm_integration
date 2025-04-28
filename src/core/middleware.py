from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.exceptions import BaseApiException


class CustomExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except BaseApiException as e:
            return JSONResponse(
                status_code=e.status_code, content={"detail": e.message}
            )

        except Exception as e:
            return JSONResponse(
                status_code=500, content={"detail": "An unexpected error occurred"}
            )
