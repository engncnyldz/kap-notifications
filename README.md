# KAP Notifications
A Python application that sends email notification for disclosures published on KAP (Public Disclosure Platform) by companies.

Using this application, you can subscribe to company's disclosures and receive emails in daily basis for disclosures published by those companies on the KAP Platform.

**Current email functionality uses AWS SES, you need to configure your AWS account to enable SES and then update below environment variables.** <br>
`AWS_ACCESS_KEY_ID` <br>
`AWS_SECRET_ACCESS_KEY` <br>
`AWS_DEFAULT_REGION` <br>
`AWS_SES_SENDER`: email address to be used as sender <br>
`AWS_SES_RECEIVER`: email address that the application will send notifications to <br>
`AWS_SES_REGION` <br>

*Email functionality can be customized in `app/utils/email.py`*

### API
Documentation is available at `/docs`

### Email Schedule
Email tasks are controlled by Celery in `app/tasks.py`. You can change its schedule. By default the task runs every day at 8:00 PM GMT+3.
Scheduled task will query the KAP endpoint url and retrieve disclosures only for the companies that you subscribed to, then create a group of email tasks. So, email send operations are controlled by Celery too.

###  `members-api` service
Used to be a database of companies exist in KAP. This service is a deployment of [KAP Members DB](https://github.com/engncnyldz/kap-members-db)

### Deployment
You can deploy the application along with its dependencies using `docker-compose.yml`
