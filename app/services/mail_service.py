import socket
from flask import current_app
from flask_mail import Message
from app import mail

# Flask-Mail doesn't expose a connection timeout, so a slow/unreachable SMTP
# server (e.g. wrong host, blocked port, or bad credentials causing a hang)
# would otherwise block the whole request indefinitely. Capping the socket
# timeout here makes a bad mail config fail fast instead of hanging the page.
_MAIL_TIMEOUT_SECONDS = 10


def _send_with_timeout(msg):
    previous_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(_MAIL_TIMEOUT_SECONDS)
        mail.send(msg)
        return True
    finally:
        socket.setdefaulttimeout(previous_timeout)


def send_registration_received_email(society):
    """Sent immediately after a society submits registration - confirms
    receipt and explains that Super Admin approval is pending."""
    try:
        msg = Message(
            subject='EcoRoute AI - Registration Received',
            recipients=[society.email],
            body=(
                f"Hi {society.secretary_name},\n\n"
                f"Thank you for registering {society.society_name} with EcoRoute AI.\n\n"
                f"Your registration (Reg. No: {society.registration_number}) has been "
                f"received and is now pending review by our Super Admin team. "
                f"You'll receive another email as soon as your account is approved "
                f"and ready to log in.\n\n"
                f"- The EcoRoute AI Team"
            )
        )
        return _send_with_timeout(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send registration email to {society.email}: {e}")
        return False


def send_registration_approved_email(society):
    """Sent when a Super Admin approves a pending society registration."""
    try:
        msg = Message(
            subject='EcoRoute AI - Your Society Has Been Approved!',
            recipients=[society.email],
            body=(
                f"Hi {society.secretary_name},\n\n"
                f"Great news! {society.society_name} has been approved by our Super Admin team. "
                f"You can now log in and start scheduling waste pickups.\n\n"
                f"Login here using the email and password you registered with.\n\n"
                f"- The EcoRoute AI Team"
            )
        )
        return _send_with_timeout(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send approval email to {society.email}: {e}")
        return False
