import subprocess
import smtplib
import socket
import os
from email.mime.text import MIMEText
import datetime

def notify(file_name, exp_name):
    
    YOUR_GOOGLE_EMAIL = 'removed due to security reasons' # The email you setup to send the email using app password
    YOUR_GOOGLE_EMAIL_APP_PASSWORD = 'removed due to security reasons'  # The app password you generated

    smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtpserver.ehlo()
    smtpserver.login(YOUR_GOOGLE_EMAIL, YOUR_GOOGLE_EMAIL_APP_PASSWORD)
    
    sent_from = YOUR_GOOGLE_EMAIL
    sent_to = sent_from  #  Send it to self (as test)
    TEXT = "New Image: \n" + exp_name + ": " + file_name
    SUBJECT = "NEW IMAGE TAKEN!"
    email_text = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT) 
    smtpserver.sendmail(sent_from, sent_to, email_text)
    
    smtpserver.close()



