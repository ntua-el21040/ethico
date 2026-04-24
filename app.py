import gradio as gr
from src.text_elements import (
    EXAMPLES,
    EXAMPLE_DILEMMA,
    INTRO_MESSAGE,
    DISCLAIMERS,
    SYSTEM_INFORMATION,
)
from src.chat import respond


with gr.Blocks(title="THUFIR") as demo:

    with gr.Sidebar(open=False):
        with gr.Tabs():
            with gr.Tab("How it works"):
                gr.Markdown(SYSTEM_INFORMATION)
            with gr.Tab("Disclaimers"):
                gr.Markdown(DISCLAIMERS)
            with gr.Tab("Example dilemma"):
                gr.Markdown(EXAMPLE_DILEMMA)
            with gr.Tab("Your dilemma"):
                dilemma_json = gr.JSON(
                    open=True, visible=True, label="Dilemma JSON", min_width=400
                )

    gr.ChatInterface(
        fn=respond,
        chatbot=gr.Chatbot(placeholder=INTRO_MESSAGE, height="70vh"),
        title="THUFIR - A Virtual Ethics Advisor",
        examples=EXAMPLES,
        additional_outputs=[dilemma_json],
    )


if __name__ == "__main__":
    demo.launch(share=False)