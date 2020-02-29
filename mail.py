from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from process import make_async
import os


@make_async
def async_send_mail(app, to_mail, mail_subject, mail_body):
        send_mail(to_mail, mail_subject, mail_body)

def send_mail(to_mail, mail_subject, mail_body):
    """
    Function to send a mail using Sendgrid API

    Parameters:
    arg1 (string): The recipient's email address.
    arg2 (string): The subject of the mail.
    arg3 (string): The body of the mail.

    """

    message = Mail(
        from_email=os.getenv('FROM_MAIL'),
        to_emails=to_mail,
        subject=mail_subject,
        html_content=mail_body)

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print("Mail to {} regarding {} successful".format(
            to_mail, mail_subject))
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print("Mail to {} regarding {} failed. ".format(
            to_mail, mail_subject))
        print(e)
