from ..utils.disclosure import beautify_disclosures, process_kap_disclosure
import httpx

kap_disclosures = [
    {
        "publishDate": "11.04.23 16:59",
        "kapTitle": "BORSA İSTANBUL A.Ş.",
        "isOldKap": "false",
        "disclosureClass": "DKB",
        "disclosureType": "DUY",
        "disclosureCategory": "STT",
        "subject": "Hak Kullanımı",
        "relatedStocks": "ALKIM, EKGYO, ENJSA, ENKAI, ESEN, MAGEN, NATEN, SODSN, TKFEN",
        "ruleTypeTerm": "-",
        "disclosureIndex": "1136451",
        "isLate": "false",
        "hasMultiLanguageSupport": "true",
        "attachmentCount": "0"
    },
    {
        "publishDate": "11.04.23 16:59",
        "kapTitle": "BORSA İSTANBUL A.Ş.",
        "isOldKap": "false",
        "disclosureClass": "DKB",
        "disclosureType": "DUY",
        "disclosureCategory": "STT",
        "subject": "İşlem Sırası Durdurma Bildirimi",
        "relatedStocks": "ALKIM, EKGYO, ENJSA, ENKAI, ESEN, MAGEN, NATEN, SODSN, TKFEN",
        "ruleTypeTerm": "-",
        "disclosureIndex": "1136451",
        "isLate": "false",
        "hasMultiLanguageSupport": "true",
        "attachmentCount": "0",
        "summary": "EUPWR.E İşlem Sırasında Devre Kesici Uygulaması Başlamıştır"
    }
    
]

kap_disclosure_page_url = "https://www.kap.org.tr/tr/Bildirim/"
kap_disclosures_query_url = "https://www.kap.org.tr/tr/api/memberDisclosureQuery"

def test_beautify_disclosures():
    disclosures = beautify_disclosures(kap_disclosures)

    assert disclosures[0].id == 1136451
    assert disclosures[0].kap_title == "BORSA İSTANBUL A.Ş."
    assert disclosures[0].summary == ""

def test_process_kap_disclosure():

    id = 1136451

    with httpx.Client() as client:
        
        r = client.get(url= kap_disclosure_page_url+str(id), follow_redirects=True)
    
    assert r.status_code == 200

def test_todays_query():

    with httpx.Client() as client:
        
        r = client.post(url= kap_disclosures_query_url, json= {
            "fromDate": "2023-04-11",
            "toDate": "2023-04-17",
            "mkkMemberOidList": [
                    "4028e4a140f2ed7201412c19687407a7",
                    "4028e4a140f2ed720140f31367840112"
                ]
            }, follow_redirects= True, timeout=10
        )
    
    assert r.status_code == 200

def test_disclosure_email_fiter():
    disclosures = beautify_disclosures(kap_disclosures)
    assert len(disclosures) == 2

    assert len(list(filter(lambda disclosure: disclosure.subject != 'İşlem Sırası Durdurma Bildirimi', disclosures))) == 1