from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse
from app.database import init_db
from app.api import api_router

app = FastAPI()

app.include_router(api_router)

@app.on_event("startup")
async def startup():
    await init_db()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={"detail": "Not authenticated"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Your API Title",
        version="1.0.0",
        description="API without visible locks for unauthorized users.",
        routes=app.routes,
    )

    # Убираем секцию security из схемы
    if "components" in openapi_schema:
        openapi_schema["components"].pop("securitySchemes", None)
    # Убираем security из маршрутов
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            method.pop("security", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
