
import os
import logging
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings

from .templates.emails.speaker_booking_notification import get_speaker_booking_notification_template
from .templates.emails.new_user_confirmation import get_new_user_confirmation_template
from .templates.emails.booking_status_update import get_booking_status_update_template
from .templates.emails.new_application_notification import get_new_application_notification_template
from .templates.emails.application_status_update import get_application_status_update_template

logger = logging.getLogger(__name__)

def _send_email_with_error_handling(subject, plain_message, from_email, recipient_list, html_message=None):
    """
    Send email with error handling that never blocks the business flow.
    Logs errors but continues execution in both development and production.
    """
    is_production = os.getenv("PRODUCTION") == "true"

    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        logger.info(f"Email sent successfully: {subject} to {recipient_list}")
    except Exception as e:
        if is_production:
            # In production, log the error but don't block the process
            logger.error(f"Failed to send email in production (continuing): {subject} to {recipient_list}. Error: {str(e)}")
        else:
            # In development, log the error but continue execution
            logger.warning(f"Failed to send email in development (continuing): {subject} to {recipient_list}. Error: {str(e)}")

def send_speaker_booking_notification(recipient_list, event_name, event_date, event_time, booker_name, username):
    subject, html_message = get_speaker_booking_notification_template(event_name, event_date, event_time, booker_name, username)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    _send_email_with_error_handling(subject, plain_message, from_email, recipient_list, html_message=html_message)

def send_new_user_confirmation(recipient_list, username):
    subject, html_message = get_new_user_confirmation_template(username)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    _send_email_with_error_handling(subject, plain_message, from_email, recipient_list, html_message=html_message)

def send_booking_status_update(recipient_list, status, event_name):
    subject, html_message = get_booking_status_update_template(status, event_name)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    _send_email_with_error_handling(subject, plain_message, from_email, recipient_list, html_message=html_message)

def send_new_application_notification(recipient_list, applicant_name, event_name):
    subject, html_message = get_new_application_notification_template(applicant_name, event_name)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    _send_email_with_error_handling(subject, plain_message, from_email, recipient_list, html_message=html_message)

def send_application_status_update(recipient_list, status, event_name, username):
    subject, html_message = get_application_status_update_template(status, event_name, username)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    _send_email_with_error_handling(subject, plain_message, from_email, recipient_list, html_message=html_message)

