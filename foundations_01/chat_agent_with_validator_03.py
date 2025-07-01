import os
from dotenv import load_dotenv
from typing import Dict, List

import gradio as gr
from openai import OpenAI

from common.constants import Constants
from common.response_formats.evaluation import Evaluation
from foundations_01.helpers import Helpers
from foundations_01.simple_chat_agent_02 import SimpleChatAgent

class ChatAgentWithValidator:

    def __init__(self, name: str, linked_in_path: str, summary_path: str):
        self._chat_agent = SimpleChatAgent()
        self._eval_model = OpenAI(base_url=Constants.GEMINI_BASE_URL, api_key=os.getenv(Constants.GOOGLE_API_KEY))
        self._name = name
        self._linked_in_path = linked_in_path
        self._summary_path = summary_path
        self._eval_system_prompt = self._get_evaluation_system_prompt(self._name,
                                                                      Helpers.get_summary_at(self._summary_path),
                                                                      Helpers.get_linked_in_details(self._linked_in_path))

    def chat(self, message, history):
        reply = self._chat_agent.chat(message, history)
        evaluation = self._evaluate(reply, message, history)

        if evaluation.is_acceptable:
            print("Passed evaluation - returning reply")
        else:
            print("Failed evaluation - retrying")
            print(evaluation.feedback)
            reply = self._chat_agent.rerun(reply, message, history, evaluation.feedback)
        return reply

    @staticmethod
    def _get_evaluation_system_prompt(name: str, summary: str, linkedin: str):
        evaluator_system_prompt = (f"You are an evaluator that decides whether a response to a question is acceptable. "
                                   f"You are provided with a conversation between a User and an Agent. "
                                   f"Your task is to decide whether the Agent's latest response is acceptable quality. "
                                   f"The Agent is playing the role of {name} and is representing {name} on their website. "
                                   f"The Agent has been instructed to be professional and engaging, as if talking to a "
                                   f"potential client or future employer who came across the website. "
                                   f"The Agent has been provided with context on {name} in the form of their summary "
                                   f"and LinkedIn details. Here's the information:")

        evaluator_system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
        evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."

    @staticmethod
    def _get_evaluator_user_prompt(reply: str, message: str, history: List[str]):
        user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
        user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
        user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
        user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
        return user_prompt


    def _evaluate(self, reply: str, message: str, history: List[Dict[str, str]]) -> Evaluation:
        messages = ([{Constants.OPEN_AI_ROLE: Constants.OPEN_AI_SYSTEM,
                      Constants.OPEN_AI_CONTENT: self._eval_system_prompt}]
                    + [{Constants.OPEN_AI_ROLE: Constants.OPEN_AI_USER,
                        Constants.OPEN_AI_CONTENT: self._get_evaluator_user_prompt(reply, message, history)}])
        response = self._open_ai.chat.completions.create(model=Constants.GEMINI_MODEL_LITE, messages=messages, response_format=Evaluation)
        return response.choices[0].message.content

if __name__ == '__main__':
    gr.ChatInterface(SimpleChatAgent('Ed Donner', './me/linkedin.pdf', './me/summary.txt').chat, type='messages').launch()
