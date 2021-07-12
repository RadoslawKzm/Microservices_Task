# built in imports
# pip3 install imports
from pydantic import BaseModel

# user created modules


class ReportLogRequestBody(BaseModel):
    level: str
    service: str
    status: str
    data: str
