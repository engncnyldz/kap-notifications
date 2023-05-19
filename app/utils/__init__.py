from ..models import DisclosureQueryModel
import datetime
import os
from ..config import logger

os.chdir(r"./app/utils")

kap_disclosures_query_url = "https://www.kap.org.tr/tr/api/memberDisclosureQuery"
kap_disclosure_page_url = "https://www.kap.org.tr/tr/Bildirim/"

with open("mail_template.html","r") as f:
    mail_template_file = f.read()