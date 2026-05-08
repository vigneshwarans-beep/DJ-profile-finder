import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, app_password, recipient_email, subject, body):
    """
    Sends an email using standard SMTP.
    Works best with Gmail App Passwords.
    """
    try:
        # Set up the SMTP server
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Attach the body of the message
        msg.attach(MIMEText(body, 'plain'))
        
        # Start server connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Secure the connection
        
        # Login to the email account
        server.login(sender_email, app_password)
        
        # Send the email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        
        # Terminate the SMTP session
        server.quit()
        return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication Error: Please check your Email and App Password."
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
