from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint
from datetime import datetime

class SubscriptionBase(BaseModel):
    stock_code: str

class SubscriptionCreate(SubscriptionBase):
    pass