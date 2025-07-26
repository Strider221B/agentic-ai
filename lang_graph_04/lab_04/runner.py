import dotenv
import uuid
from typing import Any, Dict, List, Tuple

import gradio as gr
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_core.tools.base import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph import graph
from langgraph import prebuilt
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

dotenv.load_dotenv(override=True)

from common.constants import Constants
from lang_graph_04.lab_04.evaluator_output import EvaluatorOutput
from lang_graph_04.lab_04.state import State

class Runner:

    def run(self):
        self._state_graph = self._get_state_graph()
        self._save_graph_diagram(self._state_graph)
        self._launch_chat()

    def _launch_chat(self):
        with gr.Blocks(theme=gr.themes.Default(primary_hue="emerald")) as demo:
            gr.Markdown("## Sidekick Personal Co-worker")
            thread = gr.State(self._make_thread_id())

            with gr.Row():
                chatbot = gr.Chatbot(label="Sidekick", height=300, type="messages")
            with gr.Group():
                with gr.Row():
                    message = gr.Textbox(show_label=False, placeholder="Your request to your sidekick")
                with gr.Row():
                    success_criteria = gr.Textbox(show_label=False, placeholder="What are your success critiera?")
            with gr.Row():
                reset_button = gr.Button("Reset", variant="stop")
                go_button = gr.Button("Go!", variant="primary")
            message.submit(self._process_message, [message, success_criteria, chatbot, thread], [chatbot])
            success_criteria.submit(self._process_message, [message, success_criteria, chatbot, thread], [chatbot])
            go_button.click(self._process_message, [message, success_criteria, chatbot, thread], [chatbot])
            reset_button.click(self._reset, [], [message, success_criteria, chatbot, thread])

        demo.launch()

    @classmethod
    def _get_state_graph(cls) -> CompiledStateGraph:
        graph_builder = graph.StateGraph(State)

        # Add nodes
        graph_builder.add_node("worker", cls._invoke_worker)
        graph_builder.add_node("tools", prebuilt.ToolNode(tools=cls._get_browser_tools()))
        graph_builder.add_node("evaluator", cls._invoke_evaluator)

        # Add edges
        graph_builder.add_conditional_edges("worker", cls._worker_router, {"tools": "tools", "evaluator": "evaluator"})
        graph_builder.add_edge("tools", "worker")
        graph_builder.add_conditional_edges("evaluator", cls._route_based_on_evaluation, {"worker": "worker", "END": graph.END})
        graph_builder.add_edge(graph.START, "worker")

        # Compile the graph
        memory = MemorySaver()
        return graph_builder.compile(checkpointer=memory)

    @classmethod
    def _invoke_worker(cls, state: State) -> Dict[str, BaseMessage]:
        system_message = cls._get_system_message_for_worker(state)

        if state.get('feedback_on_work'):
            system_message += cls._get_system_message_for_feedback(state)

        # Add in the system message

        found_system_message = False
        messages = state["messages"]
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = system_message
                found_system_message = True

        if not found_system_message:
            messages = [SystemMessage(content=system_message)] + messages

        # Invoke the LLM with tools
        response = cls._get_worker_llm_with_tools().invoke(messages)

        # Return updated state
        return { "messages": [response] }

    @classmethod
    def _invoke_evaluator(cls, state: State) -> State:
        last_response = state["messages"][-1].content
        system_message = cls._get_evaluator_system_message()
        user_message = cls._get_user_system_message(state, last_response)

        if state["feedback_on_work"]:
            user_message += f"Also, note that in a prior attempt from the Assistant, you provided this feedback: {state['feedback_on_work']}\n"
            user_message += "If you're seeing the Assistant repeating the same mistakes, then consider responding that user input is required."

        evaluator_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]

        eval_result = cls._get_evaluator_llm_with_output().invoke(evaluator_messages)
        new_state = {
            "messages": [{"role": "assistant", "content": f"Evaluator Feedback on this answer: {eval_result.feedback}"}],
            "feedback_on_work": eval_result.feedback,
            "success_criteria_met": eval_result.success_criteria_met,
            "user_input_needed": eval_result.user_input_needed
        }
        return new_state

    async def _process_message(self,
                               message: str,
                               success_criteria: str,
                               history: List[Dict[str, str]],
                               thread_id: str) -> List[Dict[str, str]]:

        config = {"configurable": {"thread_id": thread_id}}

        state = {
            "messages": message,
            "success_criteria": success_criteria,
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False
        }
        result = await self._state_graph.ainvoke(state, config=config)
        user = {"role": "user", "content": message}
        reply = {"role": "assistant", "content": result["messages"][-2].content}
        feedback = {"role": "assistant", "content": result["messages"][-1].content}
        return history + [user, reply, feedback]

    @classmethod
    async def _reset(cls) -> Tuple[str, str, gr.Chatbot, str]:
        return "", "", None, cls._make_thread_id()

    @classmethod
    def _get_evaluator_llm_with_output(cls) -> Runnable[LanguageModelInput, Dict | BaseModel]:
        evaluator_llm = ChatGoogleGenerativeAI(model=Constants.GEMINI_MODEL_LITE)
        return evaluator_llm.with_structured_output(EvaluatorOutput)

    @classmethod
    def _get_worker_llm_with_tools(cls) -> Runnable[LanguageModelInput, BaseMessage]:
        worker_llm = ChatGoogleGenerativeAI(model=Constants.GEMINI_MODEL_LITE)
        return worker_llm.bind_tools(cls._get_browser_tools())

    @staticmethod
    def _save_graph_diagram(state_graph: CompiledStateGraph):
        image_bytes = state_graph.get_graph().draw_mermaid_png()
        with open('./graph.png', 'wb') as f:
            f.write(image_bytes)

    @staticmethod
    def _route_based_on_evaluation(state: State) -> str:
        if state["success_criteria_met"] or state["user_input_needed"]:
            return "END"
        else:
            return "worker"

    @classmethod
    def _get_user_system_message(cls, state: State, last_response: str) -> str:
        return ("You are evaluating a conversation between the User and Assistant. "
                "You decide what action to take based on the last response from the Assistant. "
                "The entire conversation with the assistant, with the user's original request "
                f"and all replies, is: {cls._format_conversation(state['messages'])} "
                "The success criteria for this assignment is: {state['success_criteria']} "
                "And the final response from the Assistant that you are evaluating is: "
                f"{last_response} Respond with your feedback, and decide if the success "
                "criteria is met by this response. Also, decide if more user input is required, "
                "either because the assistant has a question, needs clarification, "
                "or seems to be stuck and unable to answer without help.")

    @staticmethod
    def _get_evaluator_system_message() -> str:
        return ("You are an evaluator that determines if a task has been completed successfully by an Assistant. "
                "Assess the Assistant's last response based on the given criteria. Respond with your feedback, "
                "and with your decision on whether the success criteria has been met, and whether more input "
                "is needed from the user. ")

    @staticmethod
    def _format_conversation(messages: List[Any]) -> str:
        conversation = "Conversation history:\n\n"
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                text = message.content or "[Tools use]"
                conversation += f"Assistant: {text}\n"
        return conversation

    @staticmethod
    def _worker_router(state: State) -> str:
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "evaluator"

    @staticmethod
    def _get_browser_tools() -> List[BaseTool]:
        async_browser =  create_async_playwright_browser(headless=False)
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
        return toolkit.get_tools()

    @staticmethod
    def _make_thread_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _get_system_message_for_worker(state: State) -> str:
        return ("You are a helpful assistant that can use tools to complete tasks. "
                "You keep working on a task until either you have a question or clarification for the user, or the success criteria is met. "
                "This is the success criteria: "
                f"{state['success_criteria']}. You should reply either with a question "
                 "for the user about this assignment, or with your final response. "
                "If you have a question for the user, you need to reply by clearly "
                "stating your question. An example might be: "
                "Question: please clarify whether you want a summary or a detailed answer "
                # Don't ask a question was explicitly added so that it shouldn't ask something like - can I help with anything else
                # Otherwise that'll confuse the evaluator.
                "If you've finished, reply with the final answer, and don't ask a question; simply reply with the answer.")

    @staticmethod
    def _get_system_message_for_feedback(state: State) -> str:
        return (f"Previously you thought you completed the assignment, but your reply was rejected "
                "because the success criteria was not met.Here is the feedback on why this was rejected: "
                f"{state['feedback_on_work']} With this feedback, please continue the assignment, "
                "ensuring that you meet the success criteria or have a question for the user.")

if __name__ == '__main__':
    Runner().run()
