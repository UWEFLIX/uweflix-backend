import asyncio
import logging
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict

from fastapi import HTTPException
from pydantic import EmailStr

from src.crud.models import SchedulesRecord, UsersRecord
from src.crud.queries.user import select_user_by_id
from src.schema.bookings import Booking, PersonType
from src.schema.films import Schedule
from src.schema.users import ResetRequest

logger = logging.getLogger("Email")


def convert_seconds(seconds):
    """
    Author GeeksForGeeks
    source: https://www.geeksforgeeks.org/python-program-to-convert-seconds-into-hours-minutes-and-seconds/
    """
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


class EmailClient:
    def __init__(self, server, port, username, password):
        self._server = server
        self._port = port
        self._username = username
        self._password = password
        self._tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS)

    async def password_reset_email(self, details: ResetRequest):
        await self._thread_pool_executor(
            f"Your OTP to reset Password {details.otp}",
            "Password Reset Request",
            details.email
        )

    async def _thread_pool_executor(self, content: str, subject: str, receiver: str):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                self.__send_email,
                content, subject, receiver
            )
            return result

    def __send_email(self, content: str, subject: str, receiver: str):
        email_body = MIMEText(content, "plain")
        email_message = MIMEMultipart()
        email_message["From"] = self._username
        email_message["To"] = receiver
        email_message["Subject"] = subject
        email_message.attach(email_body)

        try:
            with smtplib.SMTP(
                    self._server, self._port,
            ) as server:
                server.starttls(context=self._tls_context)
                server.login(self._username, self._password)
                server.sendmail(
                    self._username,
                    receiver,
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

    async def send_booking_email(
            self, bookings: List[Booking]
    ):
        if len(bookings) == 0:
            return

        booking = bookings[0]
        content = (f"BOOKINGS CONFIRMED\nBATCH REFERENCE: "
                   f"{booking.batch_ref}\n\n")
        show_time = booking.schedule.show_time.strftime("%d-%m-%Y %H:%M")
        content += f"SHOW TIME: {show_time}\n"
        content += f"Location: {booking.schedule.hall.hall_name}\n"
        content += f"Film: {booking.schedule.film.title}\n"
        content += f"Show Duration: {convert_seconds(booking.schedule.film.duration_sec)}\n"
        content += f"Created At: {booking.created.strftime("%d-%m-%Y %H:%M")}\n\n"

        data = await select_user_by_id(booking.assigned_user)
        user_record: UsersRecord = data["user"]

        for booking in bookings:
            content += f"SEAT NO: {booking.seat_no}\n"
            content += f"Person Type: {booking.person_type.person_type}\n"
            content += f"Ticket Price: {booking.amount}\n"
            content += f"Serial No: {booking.serial_no}\n"
            content += "\n"

        await self._thread_pool_executor(
            content, "UWEFlix Booking Confirmation", user_record.email
        )

    def send_user_created_email(self, email: EmailStr, password: str):
        asyncio.create_task(
            self._thread_pool_executor(
                f"Your UWEFlix password is {password}",
                "UWEFlix User Created",
                email
            )
        )
