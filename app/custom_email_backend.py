from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_messages(self, email_messages, request=None):
        """
        Override send_messages to ensure all emails are sent from a single account.
        """
        for message in email_messages:
            message.from_email = settings.EMAIL_HOST_USER  # Ensure the sender is the specified email

        try:
            return super().send_messages(email_messages)
        except Exception as e:
            # Add logging for better debugging
            logger.error(f"Error sending email: {str(e)}")
            raise  # Re-raise the exception after logging
