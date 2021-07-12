# built in imports
import os

import requests

# pip3 install imports
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from pydantic import BaseSettings

# user created modules
from Common_utilities.settings_utils import SettingsUtils


class Settings(BaseSettings, SettingsUtils):
    failed_attempts: int = 0
    HEALTH_CHECK_URL = os.getenv("HEALTH_CHECK_URL", False)

    COIN_DESK_URL: str = os.getenv("COIN_DESK_URL", False)
    API_CACHE_PROXY_URL = os.getenv("API_CACHE_PROXY_URL", False)


settings = Settings()
app = FastAPI()

app.on_event("startup")(settings.check_env_vars)


@app.on_event("startup")
@repeat_every(seconds=15)
async def api_updater_loop():
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={"level": "debug", "service": "API_UPDATER_main.py", "status": "200", "data": "API Alive"},
    )
    response = requests.get(f"{settings.COIN_DESK_URL}")
    requests.post(
        f"{settings.HEALTH_CHECK_URL}/report",
        json={"level": "info", "service": "API_UPDATER_main.py", "status": "200", "data": "Alive"},
    )

    if response.status_code == 200:
        requests.post(f"{settings.API_CACHE_PROXY_URL}/add", json=response.json())
        settings.failed_attempts = 0
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={"level": "debug", "service": "API_UPDATER_main.py", "status": "200", "data": "API Alive"},
        )

    if response.status_code != 200:
        settings.failed_attempts += 1
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={
                "level": "warning",
                "service": "API_UPDATER_main.py",
                "status": "200",
                "data": f"Failed to connect to API attempt: {settings.failed_attempts}",
            },
        )


@app.on_event("startup")
@repeat_every(seconds=15)
async def api_health_check():
    """
    IF API will be down, last available record will be prolonged for 1 hour to keep service alive.
    There should be proper fallback for this discussed as other API services.
    @TODO JIRA-Ticket proper fallback for API down
    :return:
    """
    if settings.failed_attempts > 3:
        requests.post(
            f"{settings.HEALTH_CHECK_URL}/report",
            json={
                "level": "critical",
                "service": "API_UPDATER_main.py",
                "status": "500",
                "data": "More than 3 failed API attempts!",
            },
        )
        last_record = requests.get(f"{settings.API_CACHE_PROXY_URL}/record")
        requests.post(f"{settings.API_CACHE_PROXY_URL}/add/?ttl=3600", json=last_record.json())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9003)
