import os

from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient

from common.constants import Constants

class GeminiClient:

    @staticmethod
    def get_gemini_chat_client(temperature: float) -> OpenAIChatCompletionClient:
        return OpenAIChatCompletionClient(model=Constants.GEMINI_MODEL_LITE,
                                          api_key=os.getenv(Constants.GOOGLE_API_KEY),
                                          model_info={'vision': True,
                                                    'function_calling': True,
                                                    'json_output': True,
                                                    'family': ModelFamily.GEMINI_2_0_FLASH,
                                                    'structured_output': True},
                                          temperature=temperature)
