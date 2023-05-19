from ..models import SubscriptionOrm, SubscriptionModel, DisclosureOrm, DisclosureModel, DisclosureQueryModel
from . import kap_disclosures_query_url, kap_disclosure_page_url, mail_template_file, logger
from ..database import SessionLocal
from typing import List
from bs4 import BeautifulSoup 
import datetime
import httpx
import json
from ..config import logger

def query_kap_disclosures():
    logger.name = __name__ 
    logger.debug("Starting today's query...")

    try:

        todays_query = DisclosureQueryModel(
            from_date=datetime.date.today().isoformat(),
            to_date=datetime.date.today().isoformat(),
            members=[],
        )
        
        session = SessionLocal()

        subscriptions = session.query(SubscriptionOrm).all()

        for sub in subscriptions:
            member = SubscriptionModel.from_orm(sub)
            todays_query.members.append(member.mkk_member_id)

        assert(len(todays_query.members) > 0), "No subscribed member!"

        logger.info(f"Today's query:\n{str(todays_query)}")

        with httpx.Client() as client:
        
            r = client.post(url= kap_disclosures_query_url, json= {
                "fromDate": todays_query.from_date,
                "toDate": todays_query.to_date,
                "mkkMemberOidList": todays_query.members
                }, follow_redirects= True, timeout=10
            )
        logger.info(f"KAP response received for today's query:\n{r.text}")
        return json.loads(r.text)

    except Exception as e:
        logger.exception(f"query_kap_disclosure failed:\n{str(e)}", exc_info=True)
        return [] 

def beautify_disclosures(disclosures):
    logger.name = __name__ 
    logger.debug("Starting beautify disclosures...")
    result = []

    for d in disclosures: 

        try:
            if int(d["disclosureIndex"]) > 0:

                disclosure_orm = DisclosureOrm (
                    id = int(d["disclosureIndex"]),
                    related_stocks = d["relatedStocks"] if d.get("relatedStocks") is not None else "",
                    publish_date = d["publishDate"] if d.get("publishDate") is not None else datetime.datetime(),
                    kap_title = d["kapTitle"] if d.get("kapTitle") is not None else "",
                    category = d["disclosureCategory"] if d.get("disclosureCategory") is not None else "",
                    summary = d["summary"] if d.get("summary") is not None else "",
                    subject = d["subject"] if d.get("subject") is not None else "",
                    updated_at = datetime.datetime.now()
                )

                result.append(disclosure_orm)
        except Exception as e:     
            logger.exception(f"Error occured during process of {str(d)}:\n{str(e)}", exc_info=True)
            continue

    return result

def save_disclosures(disclosures: List[DisclosureOrm]) -> bool:
    logger.name = __name__ 
    assert(len(disclosures) > 0), "No disclosure to save to the database!"
    logger.debug("Starting save disclosures...")
    
    try:
        session = SessionLocal()

        session.add_all(disclosures)
        session.commit()
        session.close_all()

        logger.info("Disclosures saved to the database")
        return True
    except Exception as e:
        logger.exception(f"Error occured while trying to save disclosures to the database:\n{str(e)}", exc_info=True)
        return False

def process_kap_disclosure(id: int) -> BeautifulSoup | None:
    logger.name = __name__ 
    logger.debug("Starting process kap disclosure...")
    try:

        with httpx.Client() as client:
        
            r = client.get(url= kap_disclosure_page_url+str(id), follow_redirects=True)
        
        soup = BeautifulSoup(r.text, 'html.parser')
        content = soup.find("div", attrs={"id": "disclosureContent"}).find("div", attrs={"class": "disclosureScrollableArea"})
        logger.info("KAP disclosure information fetched")
    except Exception as e:
        logger.exception(f"Error occured while fetching disclosure information from KAP:\n{str(e)}", exc_info=True)
        return None
    
    return content

def retrieve_disclosure(id: int) -> DisclosureModel | None:
    logger.name = __name__ 
    logger.debug(f"Starting retrieve disclosure {id} from database...")
    
    try:

        session = SessionLocal()

        disclosure = session.query(DisclosureOrm).filter(DisclosureOrm.id == id).first()

        logger.info(f"Disclosure {id} retrieved from the database")
        return disclosure

    except Exception as e:
        logger.exception(f"Error occured while retrieving disclosure from the database:\n{str(e)}", exc_info=True)
    

def create_mail_template(disclosure: DisclosureModel) -> BeautifulSoup | None:
    logger.name = __name__ 
    logger.debug("Starting create email template process...")
    
    kap_content = process_kap_disclosure(disclosure.id)

    if kap_content is None:
        logger.warn(f"KAP content returned none for {disclosure.id}")
        return None
   
    soup = BeautifulSoup(mail_template_file, 'html.parser')
    
    soup.find("td", attrs={"id": "relatedStocks"}).append(BeautifulSoup(f"<p>{disclosure.related_stocks}</p>", "html.parser"))
    soup.find("td", attrs={"id": "publishDate"}).append(BeautifulSoup(f"<p>{disclosure.publish_date}</p>", "html.parser"))
    soup.find("td", attrs={"id": "kapTitle"}).append(BeautifulSoup(f"<p>{disclosure.kap_title}</p>", "html.parser"))
    soup.find("td", attrs={"id": "summary"}).append(BeautifulSoup(f"<p>{disclosure.summary}</p>", "html.parser"))
    soup.find("td", attrs={"id": "subject"}).append(BeautifulSoup(f"<p>{disclosure.subject}</p>", "html.parser"))
    soup.find("div", attrs={"id":"kapArea"}).append(kap_content)
    
    logger.info(f"Email templated created for {disclosure.id}")
    return soup
    