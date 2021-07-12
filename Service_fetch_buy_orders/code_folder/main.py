# built in imports
import os
from typing import Optional

import requests

# pip3 install imports
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi_utils.tasks import repeat_every
from pydantic import BaseSettings

# user created modules
from Common_utilities.settings_utils import SettingsUtils
from Service_fetch_buy_orders.code_folder.models import GetOrdersResponseModel


class Settings(BaseSettings, SettingsUtils):
    HEALTH_CHECK_URL = os.getenv("HEALTH_CHECK_URL", False)

    DB_CACHE_PROXY_URL = os.getenv("DB_CACHE_PROXY_URL", False)


settings = Settings()
app = FastAPI()
app.on_event("startup")(settings.check_env_vars)


@app.on_event("startup")
@repeat_every(seconds=60)
async def status_report():
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={"level": "info", "service": "FETCH_BUY_ORDERS_main.py", "status": "200", "data": "Alive"},
    )


@app.get(
    "/get_orders/", responses={200: {"model": GetOrdersResponseModel}, 503: {"description": "DB Cache unavailable"}}
)
async def get_orders(start: Optional[int] = 0, page_size: Optional[int] = 10):
    response = requests.get(f"{settings.DB_CACHE_PROXY_URL}/get/?start={start}&page_size={page_size}")
    if response.status_code != 200:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={
                "level": "critical",
                "service": "FETCH_BUY_ORDERS_main.py",
                "status": "503",
                "data": "DB_CACHE unavailable",
            },
        )
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    out_json = {"data": response.json()}
    if len(response.json()) == page_size:
        out_json["_links"] = f"http://127.0.0.1:8020/get_orders/?start={start + page_size}&page_size={page_size}"
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={
            "level": "debug",
            "service": "FETCH_BUY_ORDERS_main.py",
            "status": "200",
            "data": f"obtained order {out_json}",
        },
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=out_json)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9020)
