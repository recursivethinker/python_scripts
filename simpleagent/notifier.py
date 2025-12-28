# modules/notifier.py
import os
import smtplib
import requests
from email.message import EmailMessage
from dotenv import load_dotenv

class Notifier:
    def __init__(self, preference: str):
        load_dotenv()
        self.preference = preference

    def send(self, message: str, **kwargs):
        if self.preference == 'ntfy':
            self._send_ntfy(message)
        elif self.preference == 'email':
            self._send_email(message, **kwargs)
        else:
            print("Notification preference not set or invalid. Printing to console:")
            print(message)

    def _send_ntfy(self, message: str):
        ntfy_server = os.getenv("NTFY_SERVER")
        if not ntfy_server:
            print("Error: NTFY_SERVER not configured in .env")
            return
        try:
            requests.post(ntfy_server, data=message.encode('utf-8'))
            print("ntfy notification sent.")
        except requests.exceptions.RequestException as e:
            print(f"Error sending ntfy notification: {e}")

    def _send_email(self, message: str, **kwargs):
        target_phone_number = kwargs.get('target_phone_number')
        if not target_phone_number:
            print("Error: Target phone number not provided for email notification.")
            return

        email_host = os.getenv("EMAIL_HOST")
        email_port = int(os.getenv("EMAIL_PORT", 587))
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")

        if not all([email_host, email_user, email_password]):
            print("Error: Email credentials not fully configured in .env")
            return

        msg = EmailMessage()
        msg.set_content(message)
        msg['From'] = email_user
        msg['To'] = target_phone_number

        try:
            with smtplib.SMTP(email_host, email_port) as server:
                server.starttls()
                server.login(email_user, email_password)
                server.send_message(msg)
                print("Email notification sent.")
        except smtplib.SMTPException as e:
            print(f"Error sending email: {e}")
