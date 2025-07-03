import os
from dotenv import load_dotenv

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

from common.constants import Constants

load_dotenv(override=True)

class SendGridEmail:

    _EMAIL_ID = os.environ.get(Constants.EMAIL_ID)
    _SENDGRID_KEY = os.environ.get(Constants.SENDGRID_API_KEY)

    @classmethod
    def send_email(cls, mail_body: str, subject: str, to_email_id: str = None):
        to_email_id = to_email_id if to_email_id else cls._EMAIL_ID
        sg = sendgrid.SendGridAPIClient(api_key=cls._SENDGRID_KEY)
        from_email = Email(cls._EMAIL_ID)
        to_email = To(to_email_id)
        content = Content("text/plain", mail_body)
        mail = Mail(from_email, to_email, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        print(f'Email sent to: {to_email_id} - Response Code: {response.status_code}')

if __name__ == '__main__':
    SendGridEmail.send_email('This is a test email', 'Test Mail')
