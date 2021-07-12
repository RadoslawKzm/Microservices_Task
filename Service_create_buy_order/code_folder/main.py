# built in imports
import os
from datetime import datetime, timezone
from uuid import uuid4

import requests

# pip3 install imports
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi_utils.tasks import repeat_every
from pydantic import BaseSettings

# user created modules
from Common_utilities.settings_utils import SettingsUtils
from Service_create_buy_order.code_folder.models import PlaceOrderRequestBody


class Settings(BaseSettings, SettingsUtils):
    HEALTH_CHECK_URL = os.getenv("HEALTH_CHECK_URL", False)

    API_CACHE_PROXY_URL = os.getenv("API_CACHE_PROXY_URL", False)
    DB_CACHE_PROXY_URL = os.getenv("DB_CACHE_PROXY_URL", False)


settings = Settings()
app = FastAPI()

app.on_event("startup")(settings.check_env_vars)


@app.on_event("startup")
@repeat_every(seconds=60)
async def status_report():
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={
            "level": "info",
            "service": "CREATE_BUY_ORDER_main.py",
            "status": "200",
            "data": "Create buy order alive",
        },
    )


@app.get("/")
async def root():
    """
    Function for all connections to root address with simple tutorial how to get api running
    :return: Json response with 200 code and quick tutorial how to get api running
    """
    return JSONResponse(status_code=status.HTTP_200_OK, content="Hello")


@app.post(
    "/place_order",
    responses={
        201: {"description": "Order placed successfully"},
        406: {"description": "Requested currency unsupported or amount exceeds limit"},
        503: {"description": "API cache proxy unavailable"},
    },
)
async def place_order(body: PlaceOrderRequestBody):
    """
    Function to place orders
    :param body: Json request containing currency and amount
    :return:
    """

    amount = body.amount
    currency = body.currency.upper()  # sanitizing input
    if currency not in ["EUR", "USD", "GPB"]:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={
                "level": "debug",
                "service": "CREATE_BUY_ORDER_main.py",
                "status": "406",
                "data": "Requested currency unsupported",
            },
        )
        return JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE, content="Requested currency unsupported")
    if not 0 < amount < 1_000_000_000:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={
                "level": "debug",
                "service": "CREATE_BUY_ORDER_main.py",
                "status": "406",
                "data": "Requested amount exceeds limit",
            },
        )
        return JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE, content="Requested amount exceeds limit")

    response = requests.get(f"{settings.API_CACHE_PROXY_URL}/record")

    if response.status_code != 200:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={
                "level": "critical",
                "service": "CREATE_BUY_ORDER_main.py",
                "status": "503",
                "data": "API_CACHE service unavailable",
            },
        )
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content="API Service unavailable")

    currency_dict = response.json()["bpi"][f"{currency}"]
    bitcoins = amount / currency_dict["rate_float"]
    json_ = {
        "UUID4": str(uuid4()),
        "TIMESTAMP": str(datetime.now(timezone.utc)),
        "AMOUNT": amount,
        "CURRENCY": currency,
        "EXCHANGE_RATE": currency_dict["rate_float"],
        "BITCOIN_AMOUNT": bitcoins,
    }
    posting = requests.post(f"{settings.DB_CACHE_PROXY_URL}/add", json=json_)

    if posting.status_code == 406:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={
                "level": "debug",
                "service": "CREATE_BUY_ORDER_main.py",
                "status": "406",
                "data": "Requested btc value exceeds limit",
            },
        )
        return JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE, content="Requested btc value exceeds limit")
    if posting.status_code == 201:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={
                "level": "debug",
                "service": "CREATE_BUY_ORDER_main.py",
                "status": "201",
                "data": f"Order was placed for {currency}:{amount:_.2f}",
            },
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content={"data": f"Order was placed for {currency}:{amount:_.2f}"}
        )
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={
            "level": "critical",
            "service": "CREATE_BUY_ORDER_main.py",
            "status": "503",
            "data": "API cache proxy unavailable",
        },
    )
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9001)
