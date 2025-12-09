"""
Email Service Module for Mailroom Management Application.

This module handles email notifications to residents.
Uses professor's exact email script schema.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ============================================================
# EMAIL CONFIGURATION (from keys.txt)
# ============================================================
SENDER_EMAIL = "noreply@buffteks.org"
PASSWORD = "cidm4360fall2024@*"
SMTP_SERVER = "mail.privateemail.com"
SMTP_PORT = 587


def send_notification(to_email: str, subject: str = "Package Pickup Notification") -> bool:
    """
    Send an email notification to a resident.
    
    Args:
        to_email: The recipient's email address.
        subject: The email subject line.
    
    Returns:
        True if email sent successfully, False otherwise.
    """
    # Create a MIMEMultipart email object to support multiple parts (e.g., HTML content)
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = SENDER_EMAIL
    message['To'] = to_email

    # HTML content for the email body (professor's exact template)
    html_content = """
    <html>
        <body>
            <p>Dear Resident,</p>
            <p>We have received a package for you at the leasing office. Due to limited storage 
space, please pick up your package within <strong>5 days</strong>.</p>
            <p>If the package is not picked up within this time frame, it will be returned to the 
post office.</p>
            <p>Thank you!</p>
            <p>BuffTeks Apartment Leasing Office</p>
        </body>
    </html>
    """

    # Convert the HTML content to a MIMEText object for HTML format
    html_part = MIMEText(html_content, 'html')

    # Attach the HTML part to the MIMEMultipart message
    message.attach(html_part)

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption for secure connection
            server.login(SENDER_EMAIL, PASSWORD)  # Log in with the sender's email and password
            server.send_message(message)  # Send the email message
        print(f"[OK] Email sent successfully to {to_email}!")
        return True
    except Exception as e:
        # Catch and display any exceptions that occur during the sending process
        print(f"[ERROR] Failed to send email: {str(e)}")
        return False


if __name__ == "__main__":
    # Test the email service
    test_email = "jtorres8@buffs.wtamu.edu"
    print(f"Testing email service to {test_email}...")
    send_notification(test_email)
