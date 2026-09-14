from email.message import EmailMessage
import os
import smtplib
import ssl


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


msg = EmailMessage()

msg["Subject"] = "Task App SMTPテスト"
msg["From"] = SMTP_USER
msg["To"] = SMTP_USER

msg.set_content("Task Appから送信したテストメールです。")


context = ssl.create_default_context()

with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.starttls(context=context)
    smtp.login(SMTP_USER, SMTP_PASSWORD)
    smtp.send_message(msg)

print("メール送信成功")