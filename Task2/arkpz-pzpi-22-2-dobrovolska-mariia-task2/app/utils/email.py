import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(to_email: str, subject: str, body: str):

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    from_email = "_@gmail.com"
    email_password = "your_password"

    # Настраиваем сообщение
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, email_password)
            server.send_message(message)
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

