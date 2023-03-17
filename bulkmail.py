import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define email contents
sender = os.getenv('email')
receiver = ['noticeboard@mystc.tech','noticeboard@mystc.tech']
subject = 'Subject of the email'
body = 'Body of the email'
body_html = '<html><body><h1>Body of the email in HTML</h1></body></html>'

# Create message object
msg = MIMEMultipart()
msg['From'] = sender
msg['Subject'] = subject

# Attach body to message object
msg.attach(MIMEText(body, 'plain'))
# Attach HTML part
html_part = MIMEText(body_html, 'html')
msg.attach(html_part)


# Connect to SMTP server and send email
smtp_server = 'us2.smtp.mailhostbox.com'
smtp_port = 587
smtp_username = os.getenv('email')
smtp_password = os.getenv('epsd')

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    for recipient in receiver:
        msg['To'] = recipient
        server.sendmail(sender, recipient, msg.as_string())