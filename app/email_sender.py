from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def finalize_and_send_email(request, email, form):
    """
    Finalizes and sends the email after customization.
    """
    # Create the email message
    email_message = EmailMessage(
        subject=email.subject,
        body=email.message,  # Final message after user customization
        from_email=settings.EMAIL_HOST_USER,
        to=[email.TO.email],  # Send to the intended recipient
        cc=[user.email for user in email.cc_users.all()],  # CC users
        bcc=[user.email for user in email.bcc_users.all()]  # BCC users
    )

    # Send the email
    try:
        email_message.send(fail_silently=False)
        messages.success(request, 'Email sent successfully!')
        return redirect('sent_items')  # Redirect after sending
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        messages.error(request, 'Error sending email.')
        return render(request, 'email_form.html', {'form': form, 'error': 'Error sending email.'})