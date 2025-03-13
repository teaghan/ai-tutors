import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email(subject, body, sender, sender_password, recipient):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, sender_password)
       smtp_server.sendmail(sender, recipient, msg.as_string())
    print("Message sent!")

def send_email_support(user_email, message):
    sender = 'build.ai.tutors@gmail.com'
    recipient = 'build.ai.tutors@gmail.com'
    sender_password = os.environ['EMAIL_PASSWORD']

    subject = 'AI Tutors: User Support'
    #message = message.replace('\n', '<br>')
    body = 'User: ' + user_email + '\n\n' + message
    send_email(subject, body, sender, sender_password, recipient)

def send_email_chat(teacher_email, student_name, message, html_contents, filename):
    sender = 'build.ai.tutors@gmail.com'
    recipient = teacher_email
    sender_password = os.environ['EMAIL_PASSWORD']

    msg = MIMEMultipart()
    msg['Subject'] = 'AI Tutors: Student Chat'
    msg['From'] = sender
    msg['To'] = recipient
    
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Hello 👋</h2>
        
        <p style="color: #34495e; font-size: 16px; line-height: 1.5;">
            One of your students has shared their AI Tutor conversation with you.
        </p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0; font-weight: bold; color: #2c3e50;">Student Name:</p>
            <p style="margin: 5px 0 15px 0; color: #34495e;">{student_name}</p>
            
            <p style="margin: 0; font-weight: bold; color: #2c3e50;">Student Message:</p>
            <p style="margin: 5px 0; color: #34495e; white-space: pre-wrap;">{message}</p>
        </div>
        
        <p style="color: #34495e; font-size: 16px; line-height: 1.5;">
            The complete transcript is attached!
        </p>
        
        <div style="margin-top: 30px; color: #7f8c8d; border-top: 1px solid #eee; padding-top: 20px;">
            <p style="margin: 0;">Best regards,</p>
            <p style="margin: 5px 0;">AI Tutors Team 🤖</p>
        </div>
    </div>
    """
    
    msg.attach(MIMEText(body, 'html'))
    
    # Attach the HTML content directly
    attachment = MIMEApplication(html_contents.encode('utf-8'))
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(attachment)
        
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, sender_password)
       smtp_server.sendmail(sender, recipient, msg.as_string())
    print("Message sent!")