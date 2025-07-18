import os
from dotenv import load_dotenv
from typing import Dict, List

from openai import OpenAI
import gradio as gr

from common.constants import Constants
from foundations_01.helpers import Helpers

load_dotenv(override=True)

class SimpleChatAgent:

    _MODEL_NAME = Constants.GEMINI_MODEL_LITE

    def __init__(self, name: str, linked_in_path: str, summary_path: str):
        self._open_ai = OpenAI(base_url=Constants.GEMINI_BASE_URL, api_key=os.getenv(Constants.GOOGLE_API_KEY))
        self._linked_in_path = linked_in_path
        self._summary_path = summary_path
        self._name = name
        self._system_prompt = self._get_system_prompt_for(self._name,
                                                          Helpers.get_linked_in_details(self._linked_in_path),
                                                          Helpers.get_summary_at(self._summary_path))

    def chat(self, message: str, history: List[Dict[str, str]]):
        messages = ([{Constants.OPEN_AI_ROLE: Constants.OPEN_AI_SYSTEM,
                     Constants.OPEN_AI_CONTENT: self._system_prompt}]
                     + history
                     + [{Constants.OPEN_AI_ROLE: Constants.OPEN_AI_USER, Constants.OPEN_AI_CONTENT: message}])
        response = self._open_ai.chat.completions.create(model=self._MODEL_NAME, messages=messages)
        return response.choices[0].message.content

    def rerun(self, reply: str, message: str, history: List[Dict[str, str]], feedback: str):
        updated_system_prompt = self._system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
        updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
        updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
        messages = ([{Constants.OPEN_AI_ROLE: Constants.OPEN_AI_SYSTEM,
                     Constants.OPEN_AI_CONTENT: updated_system_prompt}]
                     + history
                     + [{Constants.OPEN_AI_ROLE: Constants.OPEN_AI_USER, Constants.OPEN_AI_CONTENT: message}])
        response = self._openai.chat.completions.create(model=self._MODEL_NAME, messages=messages)
        return response.choices[0].message.content

    @staticmethod
    def _get_system_prompt_for(name: str, linked_in_details: str, summary: str) -> str:
        system_prompt = (f"You are acting as {name}. You are answering questions on {name}'s website, "
                         f"particularly questions related to {name}'s career, background, skills and experience. "
                         f"Your responsibility is to represent {name} for interactions on the website as faithfully as possible. "
                         f"You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. "
                         f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
                         f"If you don't know the answer, say so.")

        system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linked_in_details}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {name}."

        return system_prompt

if __name__ == '__main__':
    gr.ChatInterface(SimpleChatAgent('Ed Donner', './me/linkedin.pdf', './me/summary.txt').chat, type='messages').launch()
