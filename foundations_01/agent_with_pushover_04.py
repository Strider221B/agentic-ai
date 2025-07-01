import json
import os
from dotenv import load_dotenv
from typing import Dict, List

import gradio as gr
from openai import OpenAI
from pypdf import PdfReader

from common.constants import Constants
from common.tools.pushover import Pushover
from foundations_01.helpers import Helpers

load_dotenv(override=True)

class AgentWithPushover:

    def __init__(self, name: str, linked_in_path: str, summary_path: str):
        self._agent = OpenAI(base_url=Constants.GEMINI_BASE_URL, api_key=os.getenv(Constants.GOOGLE_API_KEY))
        self._tools = [{"type": "function", "function": self._get_user_details_json()},
                       {"type": "function", "function": self._get_unknown_question_json()}]
        self._name = name
        self._linked_in_path = linked_in_path
        self._summary_path = summary_path
        self._system_prompt = self._get_system_prompt(self._name,
                                                      Helpers.get_summary_at(self._summary_path),
                                                      Helpers.get_linked_in_details(self._linked_in_path))

    def chat(self, message, history):
        messages = ([{"role": "system", "content": self._system_prompt}]
                    + history
                    + [{"role": "user", "content": message}])
        done = False
        while not done:

            # This is the call to the LLM - see that we pass in the tools json

            response = self._agent.chat.completions.create(model=Constants.GEMINI_MODEL_LITE, messages=messages, tools=self._tools)

            finish_reason = response.choices[0].finish_reason
            print(f'Finish reason: {finish_reason}', flush=True)

            # If the LLM wants to call a tool, we do that!

            if finish_reason == Constants.OPEN_AI_TOOL_CALL:
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self._handle_tool_calls(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content

    @staticmethod
    def _record_user_details(email: str, name: str="Name not provided", notes: str="not provided") -> Dict[str, str]:
        Pushover.push(f"Recording interest from {name} with email {email} and notes {notes}")
        return {"recorded": "ok"}

    @staticmethod
    def _record_unknown_question(question: str) -> Dict[str, str]:
        Pushover.push(f"Recording {question} asked that I couldn't answer")
        return {"recorded": "ok"}

    @classmethod
    def _handle_tool_calls(cls, tool_calls) -> List[Dict[str, str]]:
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)

            tool = getattr(cls, tool_name)
            result = tool(**arguments) if tool else {}

            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results

    @classmethod
    def _get_system_prompt(cls, name: str, summary: str, linkedin: str) -> str:
        system_prompt = (f"You are acting as {name}. You are answering questions on {name}'s website, "
                         f"particularly questions related to {name}'s career, background, skills and experience. "
                         f"Your responsibility is to represent {name} for interactions on the website as faithfully as possible. "
                         f"You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. "
                         f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
                         f"If you don't know the answer to any question, use your {cls._record_unknown_question.__name__} tool to record the "
                         f"question that you couldn't answer, even if it's about something trivial or unrelated to career. "
                         f"If the user is engaging in discussion, try to steer them towards getting in touch via email; "
                         f"ask for their email and record it using your {cls._record_user_details.__name__} tool. ")

        system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {name}."
        return system_prompt

    @classmethod
    def _get_user_details_json(cls) -> dict:
        return {
            "name": cls._record_user_details.__name__,
            "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The email address of this user"
                    },
                    "name": {
                        "type": "string",
                        "description": "The user's name, if they provided it"
                    }
                    ,
                    "notes": {
                        "type": "string",
                        "description": "Any additional information about the conversation that's worth recording to give context"
                    }
                },
                "required": ["email"],
                "additionalProperties": False
            }
        }

    @classmethod
    def _get_unknown_question_json(cls) -> dict:
        record_unknown_question_json = {
            "name": cls._record_unknown_question.__name__,
            "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question that couldn't be answered"
                    },
                },
                "required": ["question"],
                "additionalProperties": False
            }
        }
        return record_unknown_question_json

if __name__ == '__main__':
    gr.ChatInterface(AgentWithPushover('Ed Donner', './me/linkedin.pdf', './me/summary.txt').chat, type="messages").launch()
