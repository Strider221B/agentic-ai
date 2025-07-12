from pydantic import BaseModel, Field


class PushNotificationInput(BaseModel):
    """A message to be sent to the user"""
    message: str = Field(..., description="The message to be sent to the user.")
