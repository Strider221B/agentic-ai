from typing import List, Tuple

import gradio as gr
from lang_graph_04.lab_05.sidekick import Sidekick

class App:

    @classmethod
    def launch_chat_interface(cls):
        with gr.Blocks(title="Sidekick", theme=gr.themes.Default(primary_hue="emerald")) as ui:
            gr.Markdown("## Sidekick Personal Co-Worker")
            sidekick = gr.State(delete_callback=cls._free_resources)

            with gr.Row():
                chatbot = gr.Chatbot(label="Sidekick", height=300, type="messages")
            with gr.Group():
                with gr.Row():
                    message = gr.Textbox(show_label=False, placeholder="Your request to the Sidekick")
                with gr.Row():
                    success_criteria = gr.Textbox(show_label=False, placeholder="What are your success critiera?")
            with gr.Row():
                reset_button = gr.Button("Reset", variant="stop")
                go_button = gr.Button("Go!", variant="primary")

            ui.load(cls._setup, [], [sidekick])
            message.submit(cls._process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
            success_criteria.submit(cls._process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
            go_button.click(cls._process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
            reset_button.click(cls._reset, [], [message, success_criteria, chatbot, sidekick])


        ui.launch(inbrowser=True)

    @staticmethod
    async def _setup():
        sidekick = Sidekick()
        await sidekick.setup()
        return sidekick

    @staticmethod
    async def _process_message(sidekick: Sidekick, message: str, success_criteria: str, history: List[str]):
        results = await sidekick.run_superstep(message, success_criteria, history)
        return results, sidekick

    @staticmethod
    async def _reset() -> Tuple[str, str, gr.Chatbot, Sidekick]:
        new_sidekick = Sidekick()
        await new_sidekick.setup()
        return "", "", None, new_sidekick

    @staticmethod
    def _free_resources(sidekick: Sidekick):
        print("Cleaning up")
        try:
            if sidekick:
                sidekick.free_resources()
        except Exception as e:
            print(f"Exception during cleanup: {e}")

if __name__ == '__main__':
    App.launch_chat_interface()
