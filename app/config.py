from pydantic import BaseSettings
import logging
from logging.handlers import TimedRotatingFileHandler
from enum import IntEnum

class LogLevelEnum(IntEnum):
    info = logging.INFO
    debug = logging.DEBUG
    warn = logging.WARN
    error = logging.ERROR

class Settings(BaseSettings):
    database_hostname: str = ""
    database_port: str = "1"
    database_name: str = ""
    database_username: str = ""
    database_password: str = "" 
    kap_members_app_url: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_default_region: str = ""
    aws_ses_sender: str = ""
    aws_ses_receiver: str = ""
    aws_ses_region: str = ""
    celery_broker: str = ""
    celery_backend: str = ""
    log_level: LogLevelEnum = LogLevelEnum.debug

    class Config:
        env_file = ".env"
        
settings = Settings()

logger = logging.getLogger("kap_disclosures_logger")

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = TimedRotatingFileHandler("./logs/app.log", when="midnight",backupCount=60)
file_handler.setFormatter(formatter)
file_handler.setLevel(settings.log_level)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.WARN)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
