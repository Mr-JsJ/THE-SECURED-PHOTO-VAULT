import pyotp
import smtplib
from email.message import EmailMessage
from django.conf import settings

def otp_gen(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()

def send_email(to, otp):
    msg = EmailMessage()
    subject = "Verify your email"
    body = f"Your OTP for registration is {otp}. Please do not share it with anyone."
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user = "spvproject24@gmail.com"
    msg['from'] = user
    password = ""
    
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()
