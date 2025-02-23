from flask import current_app,render_template,url_for
from flask_mail import Message
from threading import Thread
from .extensions import mail
import os

def send_async_mail(app,msg):
    with app.app_context():
        mail.send(msg)

def send_report(userEmail,username,testCode,filename):
    app = current_app._get_current_object()
    msg = Message(f"{username}'s {testCode} Report",sender='testvec26@gmail.com',recipients=[userEmail],)
    msg.body = f"""Hi {username},
Your summary report for your {testCode} has been generated!"""
    with current_app.open_resource(os.path.join(os.path.abspath("Quiz-App/reports"),filename)) as file:
        msg.attach(f"{filename}","application/pdf",file.read())
    thr = Thread(target=send_async_mail,args=[app,msg])
    thr.start()
    return thr


def send_reset_email(token,userEmail,username):
    app = current_app._get_current_object()
    msg = Message('Password Reset Request For VEC Quiz App',sender='testvec26@gmail.com',recipients=[userEmail],)
    msg.body = f"""Hello {username},

A request has been received to change the password for your VEC Quiz app account.

Click this link to reset your password: {url_for('main.reset_password_verify',token=token,_external=True)}

If you did not initiate this request, please contact us immediately in communicative english lab!

Thank you,
The Communicative English Team
"""
    msg.html = render_template('reset_email_base.html',username=username,reset_token=token)
    thr = Thread(target=send_async_mail,args=[app,msg])
    thr.start()
    return thr

def send_email_admin(token,userEmail,username):
    app = current_app._get_current_object()
    msg = Message('Password Reset Request For VEC Quiz App',sender='testvec26@gmail.com',recipients=[userEmail],)
    msg.body = f"""Hello {username},

A request has been received to change the password for your VEC Quiz app account.

Click this link to reset your password: {url_for('admin.reset_admin_password_verify',token=token,_external=True)}

If you did not initiate this request, please contact us immediately in communicative english lab!

Thank you,
The Communicative English Team
"""
    msg.html = render_template('admin/reset_email_base.html',username=username,reset_token=token)
    thr = Thread(target=send_async_mail,args=[app,msg])
    thr.start()
    return thr

def send_winner_email(userEmail,username,event_name,regno):
    app = current_app._get_current_object()
    msg = Message(f"Winner of {event_name}",sender='testvec26@gmail.com',recipients=[userEmail],)
    msg.body = f"""Hi {username},
Congratulations! You have won the {event_name} event. Your registration number is {regno}.
Thank you,
VEC Literacy Club
"""
    with current_app.open_resource(os.path.join(os.path.abspath("event_certificates/"),f"{event_name}_winner_{regno}.png")) as file:
        msg.attach(f"{event_name}_winner_{regno}.png", "image/png", file.read())
    thr = Thread(target=send_async_mail,args=[app,msg])
    thr.start()
    return thr