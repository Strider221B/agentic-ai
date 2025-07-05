from agents import Agent, GuardrailFunctionOutput, Runner, input_guardrail

from common.open_ai_gemini_client import OpenAIGeminiClient
from open_ai_02.output_types.name_check_output import NameCheckOutput

class CheckNameGuardrail:

    @input_guardrail
    async def guardrail_against_name(ctx, agent, message):
        result = await Runner.run(CheckNameGuardrail._get_agent(), message, context=ctx.context)
        is_name_in_message = result.final_output.is_name_in_message
        return GuardrailFunctionOutput(output_info={"found_name": result.final_output},tripwire_triggered=is_name_in_message)

    @staticmethod
    def _get_agent():
        return Agent(name="Name check",
                     instructions="Check if the user is including someone's personal name in what they want you to do.",
                     output_type=NameCheckOutput,
                     model=OpenAIGeminiClient.get_model())
