
import smtplib
import secrets
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPRecipientsRefused


servers = [
      {
          'hostname': 'us2.smtp.mailhostbox.com',
          'port': 587,
          'username': os.getenv('email'),
          'password': os.getenv('epsd')
      },
      {
          'hostname': 'smtp.mystc.tech',
          'port': 587,
          'username': os.getenv('email'),
          'password': os.getenv('epsd')
      },
      {
          'hostname': 'smtp-relay.sendinblue.com',
          'port': 587,
          'username': os.getenv('email'),
          'password': os.getenv('epsd3')
      },
      {
          'hostname': 'smtp.sendgrid.net',
          'port': 587,
          'username': 'apikey',
          'password': os.getenv('epsd1')
      },
      {
          'hostname': 'smtp.postmarkapp.com',
          'port': 2525,
          'username': os.getenv('epsd2'),
          'password': os.getenv('epsd2')
      }
  ]






def bulkmail(mail_address,sname,descripton):
    # Define email contents
    sender = os.getenv('email')
    
    
   
    receiver = [email['email'] for email in mail_address]
    
    subject = 'New Scheme Available'
    #body = 'Body of the email'
    
    body_html = f"""
    <html>
      <head>
        <style>
          .body {{
            font-family: Arial, sans-serif;
            margin: 0 auto;
            padding: 60px;
            background-color: #e6f2ff;
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            
          }}
          .logo {{
          
            width: auto;
            padding: 40px;
            margin: 0 auto;
          
          }}

          .container {{
            max-width: 400px;
            margin: 0 auto;
            padding: 50px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 3px 3px 9px 9px #e6e6e6;
          }}

          h2 {{
            font-size: 24px;
            margin-bottom: 10px;
            color: #002447;
          }}

          p {{
            font-size: 16px;
            margin-bottom: 20px;
            color:#808080;
          }}

          a {{
            color: #3366cc;
            text-decoration: none;
          }}
          .button {{
            background-color: #1a66ff;
            padding: 7px;
            width: 120px;
            height: 20px; 
            text-align: center;
            display: inline-block;
            font-size: 15px;
            margin: 0 auto;
            border-radius: 13px;

          }}

          /* Dark mode styles */
          @media (prefers-color-scheme: dark) {{
            body {{
              background-color: #333333;
              color: #f6f6f6;
            }}

            .container {{
              background-color: #444444;
              box-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);
            }}

            h2 {{
              color: #f6f6f6;
            }}

            p {{
              color: #cccccc;
            }}

            a {{
              color: #77aadd;
            }}
          }}
          
        </style>
      </head>
      <body class="body">
      <center>
      <div class="logo">
      <a href="https://notify.mystc.tech"><img src="https://i.ibb.co/J7rx7x4/download.png" alt="Notify" border="0" width="50px" height="auto"></a>
      <h2>Notify</h2>
      </div>
      
        <div class="container">
          <h2>{sname}</h2>
          <p>{descripton}</p>
          
            
            <a href="https://notify.mystc.tech" class="button" style="color:#ffffff;" >More Links</a>
            
        </div>
        </center>
      </body>
    </html>
    """
    
    # Create message object
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['Subject'] = subject
    
    # Attach body to message object
    #msg.attach(MIMEText(body, 'plain'))
    # Attach HTML part
    html_part = MIMEText(body_html, 'html')
    msg.attach(html_part)
    
    
    for server in servers:
      try:
        smtp_server = smtplib.SMTP(server['hostname'], server['port'])
        smtp_server.starttls()
        smtp_server.login(server['username'], server['password'])
        for recipient in receiver:
            try:
              msg['To'] = recipient
              
              smtp_server.sendmail(sender, recipient, msg.as_string())
              print("Email sent successfully")
            except SMTPRecipientsRefused as e:  
              error_message = str(e)
              if recipient in error_message:
                print(f"Failed to send email to {recipient} -Invalid email address")
              else:
                raise
            except Exception as e:
              print(f"Failed to send email to {recipient} - {str(e)}")  
        smtp_server.quit()
        print("Email sent successfully using", server['hostname'])
        break  # Exit the loop if email is sent successfully
      except smtplib.SMTPException as e:
        print("Error sending email using", server['hostname'], ":", str(e))
        print("Attempting to send using the next server")
    else:
        print("Email sending failed for all servers")


def generate(email):

    otp = secrets.randbelow(10**6)
  
    # Define email contents
    sender = os.getenv('email')
    receiver = email
    subject = 'OTP Verification'
    #body = f'Your OTP is: {otp}'
    body_html = f"""
    <html>
      <head>
        <style>
          .body {{
            font-family: Arial, sans-serif;
            margin: 0 auto;
            padding: 60px;
            background-color: #e6f2ff;
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            
          }}
          .logo {{
          
            width: auto;
            padding: 40px;
            margin: 0 auto;
          
          }}

          .container {{
            max-width: 400px;
            margin: 0 auto;
            padding: 50px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 3px 3px 9px 9px #e6e6e6;
          }}

          h2 {{
            font-size: 24px;
            margin-bottom: 10px;
            color: #002447;
          }}

          /* Dark mode styles */
          @media (prefers-color-scheme: dark) {{
            body {{
              background-color: #333333;
              color: #f6f6f6;
            }}

            .container {{
              background-color: #444444;
              box-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);
            }}

            h2 {{
              color: #f6f6f6;
            }}

          }}
          
        </style>
      </head>
      <body class="body">
      <center>
      <div class="logo">
      <a href="https://notify.mystc.tech"><img src="https://i.ibb.co/J7rx7x4/download.png" alt="Notify" border="0" width="50px" height="auto"></a>
      <h2>Notify</h2>
      </div>
      
        <div class="container">
          <h2>OTP : {otp}</h2>
             
        </div>
        </center>
      </body>
    </html>
    """

    # Create message object
    msg = MIMEMultipart()
    html_part = MIMEText(body_html, 'html')
    msg.attach(html_part)
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    for server in servers:
      try:
        smtp_server = smtplib.SMTP(server['hostname'], server['port'])
        smtp_server.starttls()
        smtp_server.login(server['username'], server['password'])
        smtp_server.sendmail(sender, receiver, msg.as_string())
        smtp_server.quit()
        print("Email sent successfully using", server['hostname'])
        break  # Exit the loop if email is sent successfully
      except smtplib.SMTPException as e:
        print("Error sending email using", server['hostname'], ":", str(e))
        print("Attempting to send using the next server")
    else:
        print("Email sending failed for all servers")    
    return otp
