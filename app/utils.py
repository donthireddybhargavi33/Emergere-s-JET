# utils.py (updated for sending emails)
from django.core.mail import EmailMessage
from django.conf import settings

def send_email(subject, message, recipient_list, cc_list=None, bcc_list=None, from_email=None):
    """
    Send an email using Django's EmailMessage class with Gmail's SMTP settings.

    Args:
        subject (str): Subject of the email.
        message (str): Body of the email.
        recipient_list (list): List of recipient email addresses.
        cc_list (list): List of CC email addresses (optional).
        bcc_list (list): List of BCC email addresses (optional).
        from_email (str): Email address of the sender. If None, uses DEFAULT_FROM_EMAIL from settings.

    Returns:
        bool: True if email is sent successfully, False otherwise.
    """
    if not from_email:
        from_email = settings.EMAIL_HOST_USER  # Use default from email if not provided
    
    email_message = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
        cc=cc_list or [],
        bcc=bcc_list or []
    )
    
    try:
        email_message.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
