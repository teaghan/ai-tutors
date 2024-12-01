import os
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, sender, sender_password, recipient):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, sender_password)
       smtp_server.sendmail(sender, recipient, msg.as_string())
    print("Message sent!")


def send_email_forgot_password(recipient, recipient_password):
    sender = 'build.ai.tutors@gmail.com'
    sender_password = os.environ['EMAIL_PASSWORD']

    subject = 'AI Tutors Password Reset'
    body = 'Your new password is: ' + recipient_password
    send_email(subject, body, sender, sender_password, recipient)