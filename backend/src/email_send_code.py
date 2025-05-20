import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv
from dotenv import load_dotenv
import datetime

from src.utils import generate_secure_code

load_dotenv()

def html_template(secret_code):
    return f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #1a5276;
                        color: white;
                        padding: 15px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        border: 1px solid #ddd;
                        padding: 20px;
                        border-radius: 0 0 5px 5px;
                        background-color: #f9f9f9;
                    }}
                    .verification-code {{
                        background-color: #eaf2f8;
                        border-left: 4px solid #3498db;
                        padding: 10px;
                        margin: 15px 0;
                        font-size: 24px;
                        font-weight: bold;
                        text-align: center;
                        color: #1a5276;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 12px;
                        color: #777;
                        text-align: center;
                    }}
                    .school-logo {{
                        text-align: center;
                        margin-bottom: 15px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>School Verification System</h2>
                </div>
                
                <div class="content">
                    <div class="school-logo">
                        <!-- Replace with your school logo or name -->
                        <h3>CRMC</h3>
                    </div>
                    
                    <p>Dear User,</p>
                    
                    <p>Please find below your verification code for school system access:</p>
                    
                    <div class="verification-code">
                        {secret_code}
                    </div>
                    
                    <p>This code is valid for 15 minutes and should not be shared with anyone.</p>
                    
                    <p>If you didn't request this code, please contact the school administration immediately.</p>
                    
                    <p>Best regards,<br>
                    School IT Department</p>
                </div>
                
                <div class="footer">
                    © {datetime.datetime.now().year} Academy High School. All rights reserved.
                </div>
            </body>
        </html>
        """
    
def send_secret_via_email(recipient_email, secret_code):
    sender_email = getenv('GMAIL_EMAIL')
    app_password = getenv('GMAIL_APP_PASSWORD')
    
    message = MIMEMultipart()
    message['From'] = 'no-reply@email.com'
    message['To'] = recipient_email
    message['Subject'] = "Your Cerification Code"

    message.attach(MIMEText(html_template(secret_code), 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        return True
    except:
        return False