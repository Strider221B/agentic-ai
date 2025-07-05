from pydantic import BaseModel

class NameCheckOutput(BaseModel):
    '''
    This class has nothing to do with guardrails. Can be used with any agents to force a
    structured output.
    '''
    is_name_in_message: bool
    name_in_message: str
