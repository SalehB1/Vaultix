# src/v1/services/email_service.py
import asyncio
from typing import List, Optional, Dict, BinaryIO
from logging import getLogger
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader

from configurations.email_config import email_conf, EmailSenderFactory, get_smtp_config, get_api_config
from src.v1.schemas.email_schema import EmailStatus

logger = getLogger(__name__)

# Configure Jinja2
jinja_env = Environment(loader=FileSystemLoader(email_conf.TEMPLATE_FOLDER))


async def send_email(
        subject: str,
        recipients: List[str],
        body: str = None,
        template_name: str = None,
        template_body: Dict = None,
        sender_name: Optional[str] = None,
        sender_email: Optional[str] = None,
        html_content: Optional[str] = None,
        html: bool = False,
        attachments: Optional[List[Dict[str, BinaryIO]]] = None
) -> EmailStatus:
    """
    Enhanced email sending function with fallback to API

    Args:
        subject: Email subject
        recipients: List of recipient email addresses
        body: Plain text body
        template_name: Name of the template file
        template_body: Variables for template
        sender_name: Custom sender name
        sender_email: Custom sender email
        html_content: Direct HTML content
        html: Whether to treat body as HTML
        attachments: List of attachments [{'filename': str, 'file': BinaryIO}]
    """
    try:
        # Create email senders
        smtp_config = get_smtp_config()
        api_config =  get_api_config()

        if sender_name:
            smtp_config['from_name'] = sender_name
            api_config['from_name'] = sender_name
        if sender_email:
            smtp_config['from_email'] = sender_email
            api_config['from_email'] = sender_email

        smtp_sender = EmailSenderFactory.create_smtp_sender(smtp_config)
        api_sender = EmailSenderFactory.create_api_sender(api_config)

        # Process template if provided
        final_html_content = html_content
        if template_name:
            try:
                template = jinja_env.get_template(template_name)
                final_html_content = template.render(**(template_body or {}))
            except Exception as e:
                logger.error(f"Template error: {str(e)}")
                raise ValueError(f"Template rendering failed: {str(e)}")

        # If body should be treated as HTML
        if html and body:
            final_html_content = body

        # Try SMTP first with retries
        smtp_success = False
        # for attempt in range(1):
        #     logger.info(f"Attempting SMTP send, attempt {attempt + 1}")
        #     if await asyncio.get_event_loop().run_in_executor(
        #             None,
        #             lambda: smtp_sender.send(
        #                 subject=subject,
        #                 recipients=recipients,
        #                 body=None if final_html_content else body,
        #                 html_content=final_html_content,
        #                 attachments=attachments
        #             )
        #     ):
        #         smtp_success = True
        #         break
        #     await asyncio.sleep(1)

        # If SMTP failed, try API
        if not smtp_success:
            logger.warning("SMTP failed, attempting API send")
            api_success = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: api_sender.send(
                    subject=subject,
                    recipients=recipients,
                    body=None if final_html_content else body,
                    html_content=final_html_content
                    # Note: API might not support attachments
                )
            )
            print(api_success)
            if not api_success:
                logger.error("Both SMTP and API delivery failed")
                raise Exception("Email delivery failed via both SMTP and API")

        return EmailStatus(
            success=True,
            message="Email sent successfully",
            status_code=200
        )

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=EmailStatus(
                success=False,
                message=str(ve),
                status_code=400,
                error=str(ve)
            ).dict()
        )

    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=EmailStatus(
                success=False,
                message="Failed to send email",
                status_code=500,
                error=str(e)
            ).model_dump()
        )

if __name__ == '__main__':
    # Method 1: Generate full number then split into dict
    # Simple usage
    send_email(
        subject="Test Email",
        recipients=["user@example.com"],
        body="Hello, world!"
    )

    # With template and attachment
