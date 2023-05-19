import boto3
from botocore.exceptions import ClientError
from ..config import settings, logger

SENDER = f"Sender Name <{settings.aws_ses_sender}>"
RECIPIENT = settings.aws_ses_receiver

# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the 
# ConfigurationSetName=CONFIGURATION_SET argument below.
#CONFIGURATION_SET = "ConfigSet"

AWS_REGION = settings.aws_ses_region
CHARSET = "UTF-8"

client = boto3.client('ses',region_name=AWS_REGION)

def send_kap_notification(subject, body_text, body_html) -> str | None:
    logger.name = __name__ 
    try:
        
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    
    except ClientError as e:
        logger.exception(f"AWS SES - send email failed:\n{str(e)}", exc_info=True)
    else:
        logger.info(f"Email sent! Message ID:\n{response['MessageId']}")
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        return response['MessageId']