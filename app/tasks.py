from celery import Celery
from celery import group
from celery.schedules import crontab
from .config import settings
from .utils.disclosure import query_kap_disclosures, beautify_disclosures, save_disclosures, create_mail_template, retrieve_disclosure
from .utils.email import send_kap_notification
from .config import logger

app = Celery("kap-disclosure-tasks",
             broker=settings.celery_broker,
             backend=settings.celery_backend
             )

app.conf.task_routes = {"app.tasks.*": {"queue": "kap-disclosure-queue"}}


app.conf.beat_schedule = {
    # Executes everyday at 20:00 UTC+3
    "process-daily-disclosures": {
        "task": "process daily disclosures",
        "schedule": crontab(hour=17, minute=0),
        "args": (),
        "options": {
            "queue": "kap-disclosure-queue"
        }
    },
}

logger.name = __name__
logger.info("Celery registered.")

@app.task(name= "process daily disclosures")
def process_daily_disclosures():
    logger.debug("Celery task process_daily_disclosures started.")

    process_result: bool | None = None

    # build query for today and call KAP API
    kap_disclosures = query_kap_disclosures()
    
    if len(kap_disclosures) > 0:

        # build proper ORM in order to be able to save to the DB        
        kap_disclosures = beautify_disclosures(kap_disclosures)
        # insert results to the DB        
        process_result = save_disclosures(kap_disclosures)

        if process_result == True:
            logger.debug("Creating email tasks...")

            # apply filter before sending email for all
            logger.debug("Applying filter before sending email...")
            kap_disclosures = list(filter(lambda disclosure: disclosure.subject != 'İşlem Sırası Durdurma Bildirimi', kap_disclosures))

            try:
                email_tasks = group(email_disclosure.s(d.id) for d in kap_disclosures)
                email_tasks.apply_async(queue="kap-disclosure-queue")

            except Exception as e:
                logger.exception(f"Email tasks creation failed:\n{str(e)}", exc_info=True)

    else:
        logger.warn("No disclosure to process")
        

@app.task(name= "email disclosure")
def email_disclosure(disclosure_id: int):

    disclosure = retrieve_disclosure(disclosure_id)

    if disclosure is None:
        logger.warn("Disclosure information couldn't be retrieved, aborting email task...")
        return

    mail_template = create_mail_template(disclosure)

    if mail_template is None:
        logger.warn("Mail template couldn't be created, aborting email task...")
        return
    
    result = send_kap_notification(subject=f"New KAP Notification - {disclosure.related_stocks}", body_text=disclosure.related_stocks, body_html=str(mail_template))

    if result is not None:
        logger.info(f"Email sent: {result}")
        return {"result": f"Email sent: {result}"}
    else:
        logger.error(f"Email couldn't be sent for the notification: {id}")