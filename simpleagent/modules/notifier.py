# modules/notifier.py
import os
import smtplib
import requests
from email.message import EmailMessage
from typing import List

class Notifier:
    def __init__(self, config: dict):
        preferences = config.get('notification_preference', [])
        # Ensure preferences is always a list for consistent processing
        if isinstance(preferences, str):
            self.preferences = [preferences]
        else:
            self.preferences = preferences
        self.config = config

    def send(self, message: str, **kwargs):
        sent_at_least_once = False
        if 'ntfy' in self.preferences:
            self._send_ntfy(message)
            sent_at_least_once = True
        if 'email' in self.preferences:
            self._send_email(message, **kwargs)
            sent_at_least_once = True

        if not sent_at_least_once:
            print("No valid notification preference configured. Printing to console:")
            print(message)

    def _send_ntfy(self, message: str):
        ntfy_server = self.config.get("NTFY_SERVER")
        if not ntfy_server:
            print("Error: NTFY_SERVER not configured in .env for ntfy notification.")
            return
        try:
            requests.post(ntfy_server, data=message.encode('utf-8'))
            print("ntfy notification sent.")
        except requests.exceptions.RequestException as e:
            print(f"Error sending ntfy notification: {e}")

    def _send_email(self, message: str, **kwargs):
        numbers_str = self.config.get('TARGET_PHONE_NUMBERS', '')
        target_phone_numbers = [num.strip() for num in numbers_str.split(',') if num.strip()]
        if not target_phone_numbers:
            print("Error: Target phone numbers not provided for email notification.")
            return

        email_host = self.config.get("EMAIL_HOST")
        email_port = int(self.config.get("EMAIL_PORT", 587))
        email_user = self.config.get("EMAIL_USER")
        email_password = self.config.get("EMAIL_PASSWORD")

        if not all([email_host, email_user, email_password]):
            print("Error: Email credentials not fully configured in .env")
            return

        try:
            with smtplib.SMTP(email_host, email_port) as server:
                server.starttls()
                server.login(email_user, email_password)
                for recipient in target_phone_numbers:
                    recipient = recipient.strip()
                    if not recipient:
                        continue
                    msg = EmailMessage()
                    msg.set_content(message)
                    msg['From'] = email_user
                    msg['To'] = recipient
                    server.send_message(msg)
                    print(f"Email notification sent to {recipient}.")
        except smtplib.SMTPException as e:
            print(f"Error sending email: {e}")
