import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_email(to_email: str, subject: str, body: str) -> None:
    sender_email = os.getenv("GMAIL_EMAIL")  # Get email from .env
    sender_password = os.getenv("GMAIL_PASSWORD")  # Get password from .env
    

    if not sender_email or not sender_password:
        raise ValueError("Email or password not found in environment variables")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
