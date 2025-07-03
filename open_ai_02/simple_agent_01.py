import os
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, trace

from common.constants import Constants

load_dotenv(override=True)

external_client = AsyncOpenAI(api_key=os.getenv(Constants.GOOGLE_API_KEY),
                              base_url=Constants.GEMINI_BASE_URL)

agent = Agent(name="Jokester",
              instructions="You are a joke teller",
              model=OpenAIChatCompletionsModel(model=Constants.GEMINI_MODEL_LITE, openai_client=external_client))

with trace("Telling a joke"):
    # await works in jupyter notebook directly as it manages event loop internally. But for
    # python script you need await inside an async method.
    # result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")
    result = Runner.run_sync(agent, "Tell a joke about Autonomous AI Agents")
    print(result.final_output)
