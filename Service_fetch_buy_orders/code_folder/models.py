# built in imports
# pip3 install imports
from pydantic import BaseModel

# user created modules


class GetOrdersResponseModel(BaseModel):
    content: dict
