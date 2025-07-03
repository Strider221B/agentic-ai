import os
from dotenv import load_dotenv

from agents import AsyncOpenAI, OpenAIChatCompletionsModel

from common.constants import Constants

load_dotenv(override=True)

class OpenAIGeminiClient:

    _EXTERNAL_CLIENT = AsyncOpenAI(api_key=os.getenv(Constants.GOOGLE_API_KEY),
                                   base_url=Constants.GEMINI_BASE_URL)

    _MODEL = OpenAIChatCompletionsModel(model=Constants.GEMINI_MODEL_LITE, openai_client=_EXTERNAL_CLIENT)

    @classmethod
    def get_model(cls) -> OpenAIChatCompletionsModel:
        return cls._MODEL
