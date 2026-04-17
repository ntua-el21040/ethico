import os
import json
import gradio as gr
from anthropic import Anthropic
from dotenv import load_dotenv
from src.validator import UtilitarianModel
from src.evaluator import evaluate_dilemma
from src.text_elements import (
    EXAMPLES, 
    EXAMPLE_DILEMMA,
    INTRO_MESSAGE, 
    DISCLAIMERS, 
    SYSTEM_INFORMATION, 
    SYSTEM_PROMPT, 
    EXPLAIN_PROMPT, 
    tools
)


load_dotenv(override=True)
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Please provide an ANTHROPIC_API_KEY in your .env file.")
    exit()
client = Anthropic(
    api_key=api_key,
)
MODEL_NAME = "claude-haiku-4-5-20251001" 
chat_messages = []
new_situation = False


def evaluate(message):
    """Handles extraction, evaluation, and explanation in a single step."""
    
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=chat_messages,
        tools=tools,
        tool_choice={"type": "tool", "name": "submit_dilemma"},
    )

    tool_use_block = response.content[0]
    tool_use_id = tool_use_block.id
    result = tool_use_block.input
    
    chat_messages.append({"role": "assistant", "content": response.content})
    
    try:
        UtilitarianModel.model_validate(result)
    except Exception as e:
        return f"Failed to validate dilemma: {e}"
        
    file_path = "./data/situation.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    evaluate_dilemma()
    global new_situation
    new_situation = True
    
    try:
        with open("./data/evaluation.json", "r", encoding="utf-8") as f:
            evaluation = json.load(f)
    except FileNotFoundError:
        return "Evaluation failed. Please try again."
    
    formatted_explain_prompt = EXPLAIN_PROMPT.format(evaluation=json.dumps(evaluation, indent=2))
    
    chat_messages.append({
        "role": "user", 
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": formatted_explain_prompt
            }
        ]
    })
    
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=chat_messages
    )
    
    reply_text = response.content[0].text
    chat_messages.append({"role": "assistant", "content": reply_text})
    return reply_text.strip()


def respond(message, history):
    chat_messages.append({"role": "user", "content": message})
    
    command = message.strip().upper()
    if command == "EVALUATE":
        return evaluate(message)
    else:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=chat_messages
        )
        
        reply_text = response.content[0].text
        chat_messages.append({"role": "assistant", "content": reply_text})
        return reply_text.strip()


with gr.Blocks() as demo:
    
    with gr.Sidebar(open=False):
        with gr.Tabs():
            with gr.Tab("How it works"):
                gr.Markdown(SYSTEM_INFORMATION)
            with gr.Tab("Disclaimers"):
                gr.Markdown(DISCLAIMERS)
            with gr.Tab("Example dilemma"):
                gr.Markdown(EXAMPLE_DILEMMA)
            with gr.Tab("Your dilemma"):
                gr.JSON(
                    value=lambda: json.load(open("./data/situation.json")) if new_situation else {},
                    every=1,
                )

    gr.ChatInterface(
        fn=respond,
        chatbot=gr.Chatbot(placeholder=INTRO_MESSAGE, height="70vh"),
        title="THUFIR - A Virtual Ethics Advisor",
        examples=EXAMPLES,
    )


if __name__ == "__main__":
    demo.queue()
    demo.launch(share=False)