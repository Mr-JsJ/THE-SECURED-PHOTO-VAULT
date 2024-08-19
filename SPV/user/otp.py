import pyotp 
import smtplib
from email.message import EmailMessage

def otp_gen(email):
    totp=pyotp.TOTP(pyotp.random_base32(),interval=60)
    otp=totp.now()
    send_email(email,otp)
    return otp

def send_email(to,otp):
    msg=EmailMessage()
    subject="Register"
    body=f"Your otp for SPV registration is {otp}.Please do not share it with any one"
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user="spvproject24@gmail.com"
    msg['from']=user
    password="ghup enlk daqk gidi"
     
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    server.quit()