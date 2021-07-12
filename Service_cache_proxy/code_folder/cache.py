# built in imports
import json
import os
import traceback

import redis
import requests

# pip3 install imports
from fastapi import status
from fastapi.responses import JSONResponse


class Cache:
    """
    Adapter Design Pattern. We are adapting redis connectivity with asynchronous execution.
    """

    def __init__(self, *, host: str, port: int, db_name: str):
        """
        Initialisation of redis communication
        :param host: Redis service hostname taken from constants.py file
        :type host: str
        :param port: Port for redis communication
        :type port: int
        :param db_name: Name of redis database, by default = 0
        :type db_name: str
        """
        self.HEALTH_CHECK_URL = os.getenv("HEALTH_CHECK_URL", False)
        self.redis = redis.Redis(host=host, port=port, db=db_name)

    def add2cache(self, *, value, ttl_sec: int = 60) -> JSONResponse:
        """
        :param value: response dict to cache
        :param ttl_sec: [optional] in seconds, by default set to 1m=60s
        :type ttl_sec: int
        :return: JSONResponse object with adequate status code and body
        """
        try:
            self.redis.set(name="record", value=f"{value}", ex=ttl_sec)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="OK")
        except redis.exceptions.ConnectionError as exc:
            requests.post(
                f"{self.HEALTH_CHECK_URL}/report",
                json={
                    "level": "error",
                    "service": "API_CACHE_main.py",
                    "status": "503",
                    "data": f"API_CACHE_cache.py:error occurred:{exc}, {traceback.format_exc()}",
                },
            )
            return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            """Pokémon catcher to catch them all and keep app running"""
            requests.post(
                f"{self.HEALTH_CHECK_URL}/report",
                json={
                    "level": "critical",
                    "service": "API_CACHE_main.py",
                    "status": "501",
                    "data": f"critical occurred:{exc}, {traceback.format_exc()}",
                },
            )
            return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED)

    def get_record_from_cache(self) -> JSONResponse(status_code=200 or 204 or 501 or 503):
        """
        :return: int or False
        """
        try:
            json_output = json.loads(self.redis.get("record").decode("UTF-8").replace("'", '"'))
            return JSONResponse(status_code=status.HTTP_200_OK, content=json_output)

        except AttributeError as exc:
            requests.post(
                f"{self.HEALTH_CHECK_URL}/report",
                json={
                    "level": "warning",
                    "service": "API_CACHE_main.py",
                    "status": "204",
                    "data": f"Redis has no content:{exc}, {traceback.format_exc()}",
                },
            )
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

        except redis.exceptions.ConnectionError as exc:
            requests.post(
                f"{self.HEALTH_CHECK_URL}/report",
                json={
                    "level": "error",
                    "service": "API_CACHE_main.py",
                    "status": "503",
                    "data": f"error occurred:{exc}, {traceback.format_exc()}",
                },
            )
            return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as exc:
            """Pokémon catcher to catch them all and keep app running"""
            requests.post(
                f"{self.HEALTH_CHECK_URL}/report",
                json={
                    "level": "critical",
                    "service": "API_CACHE_main.py",
                    "status": "501",
                    "data": f"critical occurred:{exc}, {traceback.format_exc()}",
                },
            )
            return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED)
