from . import models
from fastapi import FastAPI
from .database import engine
from .routers import disclosure, subscription
from .config import logger

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(subscription.router)
app.include_router(disclosure.router)
logger.name = __name__
logger.info("Application started.")

@app.get("/")
def root():
    
    return {"message": "Welcome to KAP Disclosures application!"}
