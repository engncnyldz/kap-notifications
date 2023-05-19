from .database import Base
from sqlalchemy import Column, String, DateTime, Integer
from pydantic import BaseModel
import datetime

class SubscriptionOrm(Base):
    __tablename__ = "kap_subscriptions"

    stock_code = Column(String, primary_key=True)
    kap_member_id = Column(String)
    mkk_member_id = Column(String)
    title = Column(String)
    updated_at = Column(DateTime)


class SubscriptionModel(BaseModel):
    stock_code: str
    kap_member_id: str
    mkk_member_id: str
    title: str
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

class DisclosureOrm(Base):
    __tablename__ = "kap_disclosures"

    id= Column(Integer, primary_key=True)
    related_stocks= Column(String)
    publish_date= Column(String)
    kap_title= Column(String)
    category= Column(String)
    summary= Column(String)
    subject= Column(String)
    updated_at = Column(DateTime)

class DisclosureModel(BaseModel):
    id: int
    related_stocks: str
    publish_date: str
    kap_title: str
    category: str
    summary: str
    subject: str
    updated_at: datetime.datetime
    
    class Config:
        orm_mode = True

class DisclosureQueryModel(BaseModel):
    from_date: str
    to_date: str
    members: list