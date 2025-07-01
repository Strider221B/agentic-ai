import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv(override=True)

from common.constants import Constants

google_api_key = os.getenv(Constants.GOOGLE_API_KEY)
gemini = OpenAI(base_url=Constants.GEMINI_BASE_URL, api_key=google_api_key)
response = gemini.chat.completions.create(model=Constants.GEMINI_MODEL_LITE,
                                          messages=[{Constants.OPEN_AI_ROLE: Constants.OPEN_AI_USER,
                                                     Constants.OPEN_AI_CONTENT: "what is 2+2?"}])
print(response.choices[0].message.content)

# Output:
# ~/Git/agentic-ai/01_open_ai$ python gemini_test_file.py
# 2 + 2 = 4 -> Gemini Flash
# 2 + 2 equals **4**. -> Gemini Flash Lite
