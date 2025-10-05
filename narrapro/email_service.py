
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings

from .templates.emails.speaker_booking_notification import get_speaker_booking_notification_template
from .templates.emails.new_user_confirmation import get_new_user_confirmation_template
from .templates.emails.booking_status_update import get_booking_status_update_template
from .templates.emails.new_application_notification import get_new_application_notification_template
from .templates.emails.application_status_update import get_application_status_update_template

def send_speaker_booking_notification(recipient_list, event_name, event_date, event_time, booker_name, username):
    subject, html_message = get_speaker_booking_notification_template(event_name, event_date, event_time, booker_name, username)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

def send_new_user_confirmation(recipient_list, username):
    subject, html_message = get_new_user_confirmation_template(username)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

def send_booking_status_update(recipient_list, status, event_name):
    subject, html_message = get_booking_status_update_template(status, event_name)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

def send_new_application_notification(recipient_list, applicant_name, event_name):
    subject, html_message = get_new_application_notification_template(applicant_name, event_name)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

def send_application_status_update(recipient_list, status, event_name, username):
    subject, html_message = get_application_status_update_template(status, event_name, username)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

