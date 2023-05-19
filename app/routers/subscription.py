from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, config
import httpx
from datetime import datetime
from ..config import logger

router = APIRouter(
    prefix="/subscription"
)

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[models.SubscriptionModel])
def get_all_subscriptions(db: Session = Depends(get_db)):
    logger.name = __name__ 
    logger.debug("GET request - get_all_subscriptions")
    try:
        subscriptions = db.query(models.SubscriptionOrm).order_by(models.SubscriptionOrm.updated_at.desc()).all()
        return subscriptions
    except Exception as e:
        logger.exception(f"get_all_subscriptions failed:\n{str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="operation failed!")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=models.SubscriptionModel)
def add_subscribe(member: schemas.SubscriptionCreate, db: Session = Depends(get_db)):
    logger.name = __name__ 
    logger.debug("POST request - add_subscribe")
    try:

        member_data = httpx.get(f"{config.settings.kap_members_app_url}/member/{member.stock_code}")
 
        if member_data.status_code != 200:
            logger.warn("Unable to retrieve data from KAP Members App")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{member.stock_code} not found")

        existing_subscription = db.query(models.SubscriptionOrm).filter(models.SubscriptionOrm.stock_code == member_data.json().get("stock_code")).first()

        if existing_subscription:
            logger.warn(f"Already subscribed to this member: {member.stock_code}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{member.stock_code} already exists")
    
        subscription = models.SubscriptionOrm(**member_data.json())
        subscription.updated_at = datetime.now()

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        logger.info(f"Subscription saved to the database: {subscription.stock_code}")
        return subscription
    
    except Exception as e:
        logger.exception(f"add_subscribe failed:\n{str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="operation failed!")
