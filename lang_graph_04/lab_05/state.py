from typing import Annotated, Any, List, Optional, TypedDict

from langgraph import graph

class State(TypedDict):
    messages: Annotated[List[Any], graph.add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool
