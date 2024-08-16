import asyncio
import logging
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import HTTPException

from src.schema.users import ResetRequest

logger = logging.getLogger("Email")


class EmailClient:
    def __init__(self, server, port, username, password):
        self._server = server
        self._port = port
        self._username = username
        self._password = password
        self._tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS)

    def _password_reset_email(self, details: ResetRequest):
        email_body = MIMEText(details.otp, "plain")
        email_message = MIMEMultipart()
        email_message["From"] = self._username
        email_message["To"] = details.email
        email_message["Subject"] = "Password Reset"
        email_message.attach(email_body)
        print(self._server)
        print(self._port)
        print(self._password)

        try:
            with smtplib.SMTP(
                    self._server, self._port,
            ) as server:
                server.starttls(context=self._tls_context)
                server.login(self._username, self._password)
                server.sendmail(
                    self._username,
                    details.email,
                    email_message.as_string()
                )
        except Exception as e:
            logger.error(f"Email error: {e}", exc_info=True)
            tz = timezone(offset=timedelta(hours=5))
            now = datetime.now(tz=tz)
            raise HTTPException(
                status_code=503,
                detail=f"Error while sending an email, timestamp: {now}"
            )

    async def password_reset_email(self, details: ResetRequest):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                self._password_reset_email,
                details
            )
