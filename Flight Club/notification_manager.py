# notification_manager.py

import os
import smtplib
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Load credentials from environment variables
TWILIO_SID = os.environ['TWILIO_SID']
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_VIRTUAL_NUMBER = os.environ["TWILIO_VIRTUAL_NUMBER"]
TWILIO_VERIFIED_NUMBER = os.environ["TWILIO_VERIFIED_NUMBER"]
TWILIO_WHATSAPP_NUMBER = os.environ["TWILIO_WHATSAPP_NUMBER"]
SMTP_ADDRESS = os.environ["EMAIL_PROVIDER_SMTP_ADDRESS"]
MY_EMAIL = os.environ["MY_EMAIL"]
MY_EMAIL_PASSWORD = os.environ["MY_EMAIL_PASSWORD"]

class NotificationManager:
    """
    This class is responsible for sending notifications with the deal flight details.
    """
    def __init__(self):
        """
        Initializes the Twilio client.
        """
        self.client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    def send_sms(self, message_body):
        """
        Sends an SMS message using the Twilio API.
        
        Args:
            message_body (str): The content of the SMS.
        """
        try:
            message = self.client.messages.create(
                from_=TWILIO_VIRTUAL_NUMBER,
                body=message_body,
                to=TWilio_VERIFIED_NUMBER
            )
            print(f"SMS sent successfully! SID: {message.sid}")
        except TwilioRestException as e:
            print(f"Error sending SMS: {e}")

    def send_whatsapp(self, message_body):
        """
        Sends a WhatsApp message using the Twilio API.
        
        Args:
            message_body (str): The content of the WhatsApp message.
        """
        try:
            message = self.client.messages.create(
                from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
                body=message_body,
                to=f'whatsapp:{TWILIO_VERIFIED_NUMBER}'
            )
            print(f"WhatsApp message sent successfully! SID: {message.sid}")
        except TwilioRestException as e:
            print(f"Error sending WhatsApp message: {e}")

    def send_emails(self, email_list, email_body):
        """
        Sends an email to a list of recipients.

        Args:
            email_list (list): A list of recipient email addresses.
            email_body (str): The content of the email body.
        """
        try:
            # Create a secure SMTP connection within a context manager
            with smtplib.SMTP(SMTP_ADDRESS, port=587) as connection:
                connection.starttls()  # Secure the connection
                connection.login(user=MY_EMAIL, password=MY_EMAIL_PASSWORD)
                for email in email_list:
                    # Construct the email message with a subject line
                    message = f"Subject: New Low Price Flight!\n\n{email_body}".encode('utf-8')
                    connection.sendmail(
                        from_addr=MY_EMAIL,
                        to_addrs=email,
                        msg=message
                    )
                    print(f"Email sent successfully to {email}")
        except smtplib.SMTPException as e:
            print(f"Error sending emails: {e}")