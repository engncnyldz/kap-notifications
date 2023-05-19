from fastapi import status, APIRouter, HTTPException, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from ..utils.disclosure import query_kap_disclosures, beautify_disclosures, save_disclosures, create_mail_template, retrieve_disclosure
from ..utils.email import send_kap_notification
from typing import List
from ..models import DisclosureModel, DisclosureOrm
from ..config import logger

router = APIRouter(
    prefix="/disclosure"
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def process_today():
    logger.name = __name__ 
    logger.debug("POST request - process_today")
    process_result: bool | None = None

    # build query for today and call KAP API
    kap_disclosures = query_kap_disclosures()

    if len(kap_disclosures) > 0:
        # build proper ORM in order to be able to save to the DB        
        kap_disclosures = beautify_disclosures(kap_disclosures)
        # insert results to the DB        
        process_result = save_disclosures(kap_disclosures)

        if process_result == True:
            return {"result": "success"}
    
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="operation failed")
        
    else:
        logger.warn("No disclosure found to process today")
        return {"result": "no disclosure to process"}


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[DisclosureModel])
def get_all_disclosures(db: Session = Depends(get_db)):
    logger.name = __name__ 
    logger.debug("GET request - get_all_disclosures")
    try:

        disclosures = db.query(DisclosureOrm).order_by(DisclosureOrm.updated_at.desc()).all()
        return disclosures
    
    except Exception as e:
        logger.exception(f"get_all_disclosures failed:\n{str(e)}", exc_info=True)


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=DisclosureModel)
def get_disclosure(id: int):
    logger.name = __name__ 
    logger.debug("GET request - get_disclosure")

    disclosure = retrieve_disclosure(id)
    
    if disclosure is None:
        logger.warn(f"No record found for: {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return disclosure
        

@router.post("/{id}", status_code=status.HTTP_200_OK)
def post_disclosure_notification(id: int, db: Session = Depends(get_db)):
    logger.name = __name__ 
    logger.debug("POST request - post_disclosure_notification")

    disclosure = retrieve_disclosure(id)

    if disclosure is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="operation failed")

    mail_template = create_mail_template(disclosure)

    if mail_template is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="operation failed")

    result = send_kap_notification(subject=f"New KAP notification from {disclosure.related_stocks}", body_text=disclosure.related_stocks, body_html=str(mail_template))
    
    if result is not None:
        logger.info(f"Email sent: {result}")
        return {"result": f"Email sent: {result}"}
    else:
        logger.error(f"Email couldn't be sent for the notification: {id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="operation failed")
    