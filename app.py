import gradio as gr
from src.text_elements import (
    EXAMPLES,
    INTRO_MESSAGE,
    SYSTEM_INFORMATION,
    DILEMMA_INTRO,
    DILEMMA_FOLLOWUP
)
from src.chat import respond

import gradio as gr

custom_css = """
.gradio-sidebar .prose ul,
.gradio-sidebar ul,
.sidebar ul {
    padding-left: 1.0em !important; 
    margin-left: 0.5em !important;
}

.gradio-sidebar .markdown,
.gradio-sidebar .prose {
    padding-left: 0.8em !important;
}
"""


with gr.Blocks(title="THUFIR") as demo:
    
    with gr.Sidebar(open=True, width=380):
        with gr.Tabs():
            with gr.Tab("How it works"):
                gr.Markdown(SYSTEM_INFORMATION)
            with gr.Tab("Your dilemma"):
                gr.Markdown(DILEMMA_INTRO)
                dilemma_json = gr.JSON(
                    open=True, visible=True, 
                    label="Dilemma JSON", 
                    min_width=400
                )
                gr.Markdown(DILEMMA_FOLLOWUP)

    gr.ChatInterface(
        fn=respond,
        chatbot=gr.Chatbot(placeholder=INTRO_MESSAGE,
                           height="70vh",
                           buttons=['copy', 'copy_all']),
        title="THUFIR - A Virtual Ethics Advisor",
        examples=EXAMPLES,
        additional_outputs=[dilemma_json],
        show_progress="hidden"
    )


if __name__ == "__main__":
    demo.launch(share=True, css=custom_css)