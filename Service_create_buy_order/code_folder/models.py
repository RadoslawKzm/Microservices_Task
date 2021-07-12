# built in imports
# pip3 install imports
from pydantic import BaseModel

# user created modules


class PlaceOrderRequestBody(BaseModel):
    currency: str
    amount: int
