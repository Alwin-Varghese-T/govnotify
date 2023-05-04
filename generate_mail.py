import smtplib
import secrets
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Connect to SMTP server and send email
smtp_server = 'us2.smtp.mailhostbox.com'
smtp_port = 587
smtp_username = os.getenv('email')
smtp_password = os.getenv('epsd')



def bulkmail(mail_adress):
    # Define email contents
    sender = os.getenv('email')
    receiver = [email['email'] for email in mail_adress]
    subject = 'Subject of the email'
    body = 'Body of the email'
    
    body_html = '<html><body><h1>HI</h1></body></html>'
    
    # Create message object
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['Subject'] = subject
    
    # Attach body to message object
    msg.attach(MIMEText(body, 'plain'))
    # Attach HTML part
    html_part = MIMEText(body_html, 'html')
    msg.attach(html_part)
    
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        for recipient in receiver:
            msg['To'] = recipient
            server.sendmail(sender, recipient, msg.as_string())


def generate(email):

    otp = secrets.randbelow(10**6)
  
    # Define email contents
    sender = os.getenv('email')
    receiver = email
    subject = 'OTP Verification'
    body = f'Your OTP is: {otp}'

    # Create message object
    msg = MIMEText(body)
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender, receiver, msg.as_string())

    print(otp)
    return otp
