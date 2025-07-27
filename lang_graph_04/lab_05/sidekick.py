import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph import graph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from common.constants import Constants
from lang_graph_04.lab_05.evaluator_output import EvaluatorOutput
from lang_graph_04.lab_05.sidekick_tools import SidekickTools
from lang_graph_04.lab_05.state import State

class Sidekick:

    def __init__(self):
        self._worker_llm_with_tools = None
        self._evaluator_llm_with_output = None
        self._tools = None
        self._llm_with_tools = None
        self._state_graph = None
        self._sidekick_id = str(uuid.uuid4())
        self._memory = MemorySaver()
        self._browser = None
        self._playwright = None

    async def setup(self):
        self._tools, self._browser, self._playwright = await SidekickTools.playwright_tools()
        self._tools += await SidekickTools.other_tools()
        worker_llm = ChatGoogleGenerativeAI(model=Constants.GEMINI_MODEL_LITE)
        self._worker_llm_with_tools = worker_llm.bind_tools(self._tools)
        evaluator_llm = ChatGoogleGenerativeAI(model=Constants.GEMINI_MODEL_LITE)
        self._evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
        await self._build_graph()

    async def run_superstep(self, message: str, success_criteria: str, history: List[str]):
        config = {"configurable": {"thread_id": self._sidekick_id}}

        state = {
            "messages": message,
            "success_criteria": success_criteria or "The answer should be clear and accurate",
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False
        }
        result = await self._state_graph.ainvoke(state, config=config)
        user = {"role": "user", "content": message}
        reply = {"role": "assistant", "content": result["messages"][-2].content}
        feedback = {"role": "assistant", "content": result["messages"][-1].content}
        return history + [user, reply, feedback]

    def cleanup(self):
        if self._browser:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._browser.close())
                if self._playwright:
                    loop.create_task(self._playwright.stop())
            except RuntimeError:
                # If no loop is running, do a direct run
                asyncio.run(self._browser.close())
                if self._playwright:
                    asyncio.run(self._playwright.stop())

    def _worker(self, state: State) -> Dict[str, Any]:
        system_message = f"""You are a helpful assistant that can use tools to complete tasks.
    You keep working on a task until either you have a question or clarification for the user, or the success criteria is met.
    You have many tools to help you, including tools to browse the internet, navigating and retrieving web pages.
    You have a tool to run python code, but note that you would need to include a print() statement if you wanted to receive output.
    The current date and time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    This is the success criteria:
    {state['success_criteria']}
    You should reply either with a question for the user about this assignment, or with your final response.
    If you have a question for the user, you need to reply by clearly stating your question. An example might be:

    Question: please clarify whether you want a summary or a detailed answer

    If you've finished, reply with the final answer, and don't ask a question; simply reply with the answer.
    """

        if state.get("feedback_on_work"):
            system_message += f"""
    Previously you thought you completed the assignment, but your reply was rejected because the success criteria was not met.
    Here is the feedback on why this was rejected:
    {state['feedback_on_work']}
    With this feedback, please continue the assignment, ensuring that you meet the success criteria or have a question for the user."""

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
        response = self._worker_llm_with_tools.invoke(messages)

        # Return updated state
        return {
            "messages": [response],
        }


    def _worker_router(self, state: State) -> str:
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "evaluator"

    def _format_conversation(self, messages: List[Any]) -> str:
        conversation = "Conversation history:\n\n"
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                text = message.content or "[Tools use]"
                conversation += f"Assistant: {text}\n"
        return conversation

    def _evaluator(self, state: State) -> State:
        last_response = state["messages"][-1].content

        system_message = f"""You are an evaluator that determines if a task has been completed successfully by an Assistant.
    Assess the Assistant's last response based on the given criteria. Respond with your feedback, and with your decision on whether the success criteria has been met,
    and whether more input is needed from the user."""

        user_message = f"""You are evaluating a conversation between the User and Assistant. You decide what action to take based on the last response from the Assistant.

    The entire conversation with the assistant, with the user's original request and all replies, is:
    {self._format_conversation(state['messages'])}

    The success criteria for this assignment is:
    {state['success_criteria']}

    And the final response from the Assistant that you are evaluating is:
    {last_response}

    Respond with your feedback, and decide if the success criteria is met by this response.
    Also, decide if more user input is required, either because the assistant has a question, needs clarification, or seems to be stuck and unable to answer without help.

    The Assistant has access to a tool to write files. If the Assistant says they have written a file, then you can assume they have done so.
    Overall you should give the Assistant the benefit of the doubt if they say they've done something. But you should reject if you feel that more work should go into this.

    """
        if state["feedback_on_work"]:
            user_message += f"Also, note that in a prior attempt from the Assistant, you provided this feedback: {state['feedback_on_work']}\n"
            user_message += "If you're seeing the Assistant repeating the same mistakes, then consider responding that user input is required."

        evaluator_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]

        eval_result = self._evaluator_llm_with_output.invoke(evaluator_messages)
        new_state = {
            "messages": [{"role": "assistant", "content": f"Evaluator Feedback on this answer: {eval_result.feedback}"}],
            "feedback_on_work": eval_result.feedback,
            "success_criteria_met": eval_result.success_criteria_met,
            "user_input_needed": eval_result.user_input_needed
        }
        return new_state

    def _route_based_on_evaluation(self, state: State) -> str:
        if state["success_criteria_met"] or state["user_input_needed"]:
            return "END"
        else:
            return "worker"


    async def _build_graph(self):
        # Set up Graph Builder with State
        graph_builder = graph.StateGraph(State)

        # Add nodes
        graph_builder.add_node("worker", self._worker)
        graph_builder.add_node("tools", ToolNode(tools=self._tools))
        graph_builder.add_node("evaluator", self._evaluator)

        # Add edges
        graph_builder.add_conditional_edges("worker", self._worker_router, {"tools": "tools", "evaluator": "evaluator"})
        graph_builder.add_edge("tools", "worker")
        graph_builder.add_conditional_edges("evaluator", self._route_based_on_evaluation, {"worker": "worker", "END": graph.END})
        graph_builder.add_edge(graph.START, "worker")

        # Compile the graph
        self._state_graph = graph_builder.compile(checkpointer=self._memory)
