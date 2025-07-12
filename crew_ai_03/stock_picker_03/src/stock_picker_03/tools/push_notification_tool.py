from crewai.tools import BaseTool
from pydantic import BaseModel
from typing import Type

from common.response_formats.push_notification_input import PushNotificationInput
from common.tools.pushover import Pushover

class PushNotificationTool(BaseTool):
    name: str = "Send a push notification"
    description: str = (
        "This tool is used to send a push notification to the user."
    )
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, message: str) -> str: # Parameter name should match the field name in the input format / args_schema
        Pushover.push(message)
