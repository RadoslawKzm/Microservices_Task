# built in imports
import os
from datetime import datetime, timezone

import requests

# pip3 install imports
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_utils.tasks import repeat_every
from pydantic import BaseSettings
from sqlalchemy.sql import func

# user created modules
from Common_utilities.settings_utils import SettingsUtils
from Service_db_proxy.code_folder.database_connector import DbContext
from Service_db_proxy.code_folder.database_tables import BaseTable
from Service_db_proxy.code_folder.models import GetResponseModel


class Settings(BaseSettings, SettingsUtils):
    HEALTH_CHECK_URL = os.getenv("HEALTH_CHECK_URL", False)

    POSTGRES_USER = os.getenv("POSTGRES_USER", False)
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", False)
    POSTGRES_HOSTNAME = os.getenv("POSTGRES_HOSTNAME", False)
    POSTGRES_DB = os.getenv("POSTGRES_DB", False)


settings = Settings()
app = FastAPI()

app.on_event("startup")(settings.check_env_vars)


@app.on_event("startup")
async def populate_db():
    # only for exercise purposes, in production we would have established database
    exc = True
    while exc:
        try:
            BaseTable.__table__.create(bind=DbContext.get_engine(), checkfirst=True)
            exc = False
        except Exception:
            pass


@app.on_event("startup")
@repeat_every(seconds=60)
async def status_report():
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={"level": "info", "service": "DB_PROXY_main.py", "status": "200", "data": "DB_PROXY alive"},
    )


@app.get(
    "/get/",
    responses={
        200: {"model": GetResponseModel},
        503: {"description": "Error while querying database for given spectrum"},
    },
)
async def read_item(start: int = 0, page_size: int = 10):
    context_mgr = DbContext(bind=DbContext.get_engine(), status_success=200, status_fail=503)
    with context_mgr as session:
        results = session.query(BaseTable).order_by(BaseTable.TIMESTAMP.desc()).limit(page_size).offset(start)
        results = [row.as_dict() for row in results]
    if context_mgr.status_code == 200:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={"level": "debug", "service": "DB_PROXY_main.py", "status": "200", "data": f"{results}"},
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content=results)
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={"level": "critical", "service": "DB_PROXY_main.py", "status": "503", "data": f"{context_mgr.json}"},
    )
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@app.post(
    "/add/",
    responses={
        201: {"description": "Created record in DB"},
        406: {"description": "BTC amount in db + new transaction exceeds 100BTC limit from exercise"},
        409: {"description": "Conflict while adding record to database"},
        503: {"description": "Database is not responding"},
    },
)
async def add_record(request: Request):
    input_json = await request.json()

    # Validation if input don't exceed 100BTC in db
    context_mgr = DbContext(bind=DbContext.get_engine(), status_success=200, status_fail=503)
    with context_mgr as session:
        bitcoins_in_db = session.query(func.sum(BaseTable.BITCOIN_AMOUNT)).first()[0]
    if context_mgr.status_code == 503:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={"level": "critical", "service": "DB_PROXY_main.py", "status": "503", "data": f"{context_mgr.json}"},
        )
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    if not bitcoins_in_db:
        bitcoins_in_db = 0
    if float(bitcoins_in_db) + input_json["BITCOIN_AMOUNT"] > 100:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={
                "level": "warning",
                "service": "DB_PROXY_main.py",
                "status": "406",
                "data": "database is full of bitcoins (100BTC), denying new requests",
            },
        ),
        return JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE)

    # Creating buy order
    context_mgr = DbContext(bind=DbContext.get_engine(), status_success=200, status_fail=status.HTTP_409_CONFLICT)
    with context_mgr as session:
        session.add(
            BaseTable(
                UUID=input_json["UUID4"],
                TIMESTAMP=datetime.now(timezone.utc),
                AMOUNT=input_json["AMOUNT"],
                CURRENCY=input_json["CURRENCY"],
                EXCHANGE_RATE=input_json["EXCHANGE_RATE"],
                BITCOIN_AMOUNT=input_json["BITCOIN_AMOUNT"],
            )
        )
        session.flush()
    if context_mgr.status_code == 409:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={"level": "critical", "service": "DB_PROXY_main.py", "status": "409", "data": f"{context_mgr.json}"},
        )
        return JSONResponse(status_code=status.HTTP_409_CONFLICT)
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={"level": "debug", "service": "DB_PROXY_main.py", "status": "201", "data": "Created"},
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9010)
