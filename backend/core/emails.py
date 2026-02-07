import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMessage
from .models import EmailLog

logger = logging.getLogger(__name__)


class ConsoleEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        count = 0
        for message in email_messages:
            if not isinstance(message, EmailMessage):
                continue
            logger.info("Email to %s: %s\n%s", message.to, message.subject, message.body)
            EmailLog.objects.create(
                to_address=",".join(message.to or []),
                subject=message.subject or "",
                body=message.body or "",
            )
            count += 1
        return count
