# built in imports
import os

# pip3 install imports
import requests


class SettingsUtils:
    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if k.isupper()}

    def check_env_vars(self):
        HEALTH_CHECK_URL = os.getenv("HEALTH_CHECK_URL", False)
        for env_var, value in self.as_dict().items():
            if not value:
                print(f"\n\n{'#' * 30}\n\n\nTurning on sirens, defcon 1. {env_var} is not set!!!\n\n\n{'#' * 30}\n")
                requests.post(
                    f"{HEALTH_CHECK_URL}/report",
                    json={
                        "level": "critical",
                        "service": f"{__name__}",
                        "status": "500",
                        "data": f"{env_var} is not set!!!",
                    },
                )
