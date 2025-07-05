import os
from dotenv import load_dotenv

import sendgrid
from agents import Agent, OpenAIChatCompletionsModel, function_tool
from sendgrid.helpers.mail import Mail, Email, To, Content

from common.constants import Constants

load_dotenv(override=True)

class SendGridEmail:

    EMAIL_TYPE_HTML = 'text/html'
    EMAIL_TYPE_PLAIN = 'text/plain'
    _EMAIL_ID = os.environ.get(Constants.EMAIL_ID)
    _SENDGRID_KEY = os.environ.get(Constants.SENDGRID_API_KEY)

    @staticmethod
    @function_tool
    def send_email_tool(subject: str, mail_body: str):
        # function_tool cannot be called directly so have split it into 2 separate methods.
        SendGridEmail.send_email(subject, mail_body, SendGridEmail.EMAIL_TYPE_PLAIN, None)

    @staticmethod
    @function_tool
    def send_email_tool_html(subject: str, mail_body: str):
        # function_tool cannot be called directly so have split it into 2 separate methods.
        SendGridEmail.send_email(subject, mail_body, SendGridEmail.EMAIL_TYPE_HTML, None)

    @classmethod
    def get_html_converter_tool(cls, model: OpenAIChatCompletionsModel):
        html_converter = Agent(name="HTML email body converter",
                               instructions=cls._get_html_email_instructions(),
                               model=model)
        html_tool = html_converter.as_tool(tool_name="html_converter",
                                           tool_description="Convert a text email body to an HTML email body")
        return html_tool

    @classmethod
    def send_email(cls, subject: str, mail_body: str, email_type: str, to_email_id: str = None):
        to_email_id = to_email_id if to_email_id else cls._EMAIL_ID
        sg = sendgrid.SendGridAPIClient(api_key=cls._SENDGRID_KEY)
        from_email = Email(cls._EMAIL_ID)
        to_email = To(to_email_id)
        content = Content(email_type, mail_body)
        mail = Mail(from_email, to_email, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        print(f'Email sent to: {to_email_id} - Response Code: {response.status_code}')

    @staticmethod
    def _get_html_email_instructions() -> str:
        return ("You can convert a text email body to an HTML email body. "
                "You are given a text email body which might have some markdown "
                "and you need to convert it to an HTML email body with simple, clear, compelling layout and design.")

if __name__ == '__main__':
    SendGridEmail.send_email('This is a test email', 'Test Mail')
