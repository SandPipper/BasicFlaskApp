from flask import current_app, render_template
from flask_mail import Message
from .decorators import async
from . import mail


@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app_config['BLOG_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.configp['BLOG_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    send_async_email(app, msg)
