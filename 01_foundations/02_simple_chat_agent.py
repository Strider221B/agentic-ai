import os
from dotenv import load_dotenv
from typing import List

from openai import OpenAI
from pypdf import PdfReader
import gradio as gr

from common.constants import Constants

load_dotenv(override=True)

class SimpleChatAgent:

    def __init__(self):
        self._open_ai = OpenAI(base_url=Constants.GEMINI_BASE_URL, api_key=os.getenv(Constants.GOOGLE_API_KEY))
        self._linked_in_path = './me/linkedin.pdf'
        self._summary_path = './me/summary.txt'
        self._name = 'Ed Donner'
        self._system_prompt = self._get_system_prompt_for(self._name,
                                                          self._get_linked_in_details(self._linked_in_path),
                                                          self._get_summary_at(self._summary_path))

    def chat(self, message: str, history: List[str]):
        messages = ([{Constants.OPEN_AI_ROLE: Constants.OPEN_AI_SYSTEM,
                     Constants.OPEN_AI_CONTENT: self._system_prompt}]
                     + history
                     + [{Constants.OPEN_AI_ROLE: Constants.OPEN_AI_USER, Constants.OPEN_AI_CONTENT: message}])
        response = self._open_ai.chat.completions.create(model=Constants.GEMINI_MODEL_LITE, messages=messages)
        return response.choices[0].message.content

    @staticmethod
    def _get_linked_in_details(profile_path: str) -> str:
        reader = PdfReader(profile_path)
        linkedin = ''
        for page in reader.pages:
            text = page.extract_text()
            if text:
                linkedin += text
        return linkedin

    @staticmethod
    def _get_summary_at(path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            summary = f.read()
        return summary

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
    gr.ChatInterface(SimpleChatAgent().chat, type='messages').launch()
