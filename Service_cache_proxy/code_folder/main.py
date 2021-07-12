# built in imports
import json
import os
from typing import Optional

import requests

# pip3 install imports
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_utils.tasks import repeat_every
from pydantic import BaseSettings

# user created modules
from Common_utilities.settings_utils import SettingsUtils
from Service_cache_proxy.code_folder.cache import Cache


class Settings(BaseSettings, SettingsUtils):
    HEALTH_CHECK_URL = os.getenv("HEALTH_CHECK_URL", False)

    CACHE_HOST: str = os.getenv("CACHE_HOST", False)
    CACHE_PORT: int = os.getenv("CACHE_PORT", False)
    CACHE_DB_NAME_1: str = os.getenv("CACHE_DB_NAME_1", False)


settings = Settings()
cache = Cache(host=settings.CACHE_HOST, port=settings.CACHE_PORT, db_name=settings.CACHE_DB_NAME_1)
app = FastAPI()
app.on_event("startup")(settings.check_env_vars)


@app.on_event("startup")
@repeat_every(seconds=60)
async def status_report():
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={"level": "debug", "service": "API_CACHE_main.py", "status": "200", "data": "Alive"},
    )


@app.get(
    "/record",
    responses={
        200: {"description": "Successfully obtained data from cache"},
        204: {"description": "Cache has no content"},
        501: {"description": "Unsupported exception in Redis, log sent to health check"},
        503: {"description": "Redis server unavailable"},
    },
)
async def get_record() -> JSONResponse:
    response = cache.get_record_from_cache()
    if response.status_code == 200:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={"level": "debug", "service": "API_CACHE_main.py", "status": "200", "data": f"{response.body}"},
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=json.loads(response.body))
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={"level": "error", "service": "API_CACHE_main.py", "status": f"{response.status_code}", "data": ""},
    )
    return JSONResponse(status_code=response.status_code)


@app.post(
    "/add/",
    responses={
        201: {"description": "Redis updated successfully"},
        501: {"description": "Unsupported exception in Redis, log sent to health check"},
        503: {"description": "Redis server unavailable"},
    },
)
async def add_to_cache(request: Request, ttl: Optional[int] = 60) -> JSONResponse:
    """Consciously added ttl as query param to post request.
    It was only one week exercise and had no time to create full pledged json serializer"""
    input_json = await request.json()
    response = cache.add2cache(value=input_json, ttl_sec=ttl)
    if response.status_code == 201:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={"level": "debug", "service": "API_CACHE_main.py", "status": "201", "data": "Created"},
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=json.loads(response.body))
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={"level": "debug", "service": "API_CACHE_main.py", "status": f"{response.status_code}", "data": ""},
    )
    return JSONResponse(status_code=response.status_code)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9002)
