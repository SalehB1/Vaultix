import os
from fastapi_mail import FastMail, ConnectionConfig
from configurations.environments import Values
import smtplib
from email.message import EmailMessage
import requests
from typing import List, Optional, Dict, BinaryIO
from logging import getLogger
from abc import ABC, abstractmethod

logger = getLogger(__name__)

# FastMail Configuration
email_conf = ConnectionConfig(
    MAIL_USERNAME=Values.MAIL_USERNAME,
    MAIL_PASSWORD=Values.MAIL_PASSWORD,
    MAIL_FROM=Values.MAIL_FROM,
    MAIL_PORT=Values.MAIL_PORT,
    MAIL_SERVER=Values.MAIL_SERVER,
    MAIL_FROM_NAME=Values.MAIL_FROM_NAME,
    MAIL_STARTTLS=Values.MAIL_STARTTLS,
    MAIL_SSL_TLS=Values.MAIL_SSL_TLS,
    USE_CREDENTIALS=Values.USE_CREDENTIALS,
    TEMPLATE_FOLDER=Values.TEMPLATE_FOLDER
)

fastmail = FastMail(email_conf)


# Email Sender Base Class
class EmailSenderBase(ABC):
    """Abstract base class for email senders"""

    @abstractmethod
    def send(
            self,
            subject: str,
            recipients: List[str],
            body: Optional[str] = None,
            html_content: Optional[str] = None,
            attachments: Optional[List[Dict[str, BinaryIO]]] = None
    ) -> bool:
        pass


# SMTP Sender Implementation
class SMTPEmailSender(EmailSenderBase):
    """SMTP implementation of email sender"""

    def __init__(self, config: Dict):
        self.config = config

    def send(
            self,
            subject: str,
            recipients: List[str],
            body: Optional[str] = None,
            html_content: Optional[str] = None,
            attachments: Optional[List[Dict[str, BinaryIO]]] = None
    ) -> bool:
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
            msg['To'] = ', '.join(recipients)

            # Set content
            if body:
                msg.set_content(body)
            if html_content:
                msg.add_alternative(html_content, subtype='html')

            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    file_data = attachment['file'].read()
                    msg.add_attachment(
                        file_data,
                        maintype='application',
                        subtype='octet-stream',
                        filename=attachment['filename']
                    )

            # Send email
            with smtplib.SMTP(self.config['server'], self.config['port']) as server:
                server.starttls()
                server.login(self.config['username'], self.config['password'])
                server.send_message(msg)

            return True

        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False


# API Sender Implementation
class APIEmailSender(EmailSenderBase):
    """API implementation of email sender"""

    def __init__(self, config: Dict):
        self.config = config

    def send(
            self,
            subject: str,
            recipients: List[str],
            body: Optional[str] = None,
            html_content: Optional[str] = None,
            attachments: Optional[List[Dict[str, BinaryIO]]] = None
    ) -> bool:
        try:
            recipients_list = [
                {'email': email, 'name': email.split('@')[0]}
                for email in recipients
            ]

            email_data = {
                'from': {
                    'name': self.config['from_name'],
                    'email': self.config['from_email'],
                },
                'recipients': recipients_list,
                'content': {
                    'subject': subject,
                    'text_body': body if body else '',
                    'html_body': html_content if html_content else '',
                },
            }

            headers = {
                'X-Api-Key': self.config['api_key'],
                'Content-Type': 'application/json'
            }
            print(email_data)
            response = requests.post(
                self.config['url'],
                json=email_data,
                headers=headers
            )
            print(response.text)
            return response.status_code == 200

        except Exception as e:
            print(e)
            logger.error(f"API error: {str(e)}")
            return False


# Email Sender Factory
class EmailSenderFactory:
    """Factory class to create email senders"""

    @staticmethod
    def create_smtp_sender(config: Dict) -> SMTPEmailSender:
        return SMTPEmailSender(config)

    @staticmethod
    def create_api_sender(config: Dict) -> APIEmailSender:
        return APIEmailSender(config)


# Configuration Helper Functions
def get_smtp_config() -> dict:
    return {
        'server': email_conf.MAIL_SERVER,
        'port': email_conf.MAIL_PORT,
        'username': email_conf.MAIL_USERNAME,
        'password': email_conf.MAIL_PASSWORD,
        'from_email': email_conf.MAIL_FROM,
        'from_name': email_conf.MAIL_FROM_NAME
    }


def get_api_config() -> dict:
    info = {
        'url': Values.EMAIL_API_URL,  # Make sure to add this to your Values
        'api_key': Values.EMAIL_API_KEY,  # Make sure to add this to your Values
        'from_email': email_conf.MAIL_FROM,
        'from_name': email_conf.MAIL_FROM_NAME
    }
    print(info)
    return info
