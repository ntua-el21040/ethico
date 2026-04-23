import json
import gradio as gr
from anthropic import Anthropic, APIError
from src.evaluator import evaluate_dilemma
from src.validator import (
    Settings,
    KantianModel,
)
from src.text_elements import (
    KANTIAN_PROMPT,
    EXPLAIN_PROMPT,
    tools,
)

settings = Settings()
client = Anthropic(
    api_key=settings.anthropic_api_key,
)
MODEL_NAME = "claude-haiku-4-5-20251001"
chat_messages = []


def evaluate(message):
    """
    Extracts the dilemma json from chat history, evaluates it, and explains the resulting evaluation.
    """
    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=KANTIAN_PROMPT,
            messages=chat_messages,
            tools=tools,
            tool_choice={"type": "tool", "name": "extract_kantian_dilemma"},
        )
    except APIError as e:
        raise RuntimeError(f"API request failed: {e}")

    tool_use_block = response.content[0]
    tool_use_id = tool_use_block.id
    result = tool_use_block.input

    try:
        KantianModel.model_validate(result)
    except Exception:
        raise gr.Error(
            "There was an error creating the dilema. Please ensure your input is well-formed and try again."
        )
    
    chat_messages.append({"role": "assistant", "content": response.content})

    try:
        file_path = "./data/situation.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    except OSError as e:
        raise gr.Error("Failed to save the dilemma. Check file permissions.")

    try:
        evaluate_dilemma()
    except Exception as e:
        raise gr.Error(
            "The ethics engine could not evaluate this dilemma. Please ensure your input is well-formed and try again."
        )

    try:
        with open("./data/evaluation.json", "r", encoding="utf-8") as f:
            evaluation = json.load(f)
    except Exception as e:
        raise gr.Error(
            "There awas an error loading the evaluation results. Please try again."
        )

    formatted_explain_prompt = EXPLAIN_PROMPT.format(
        evaluation=json.dumps(evaluation, indent=2)
    )

    chat_messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": formatted_explain_prompt,
                }
            ],
        }
    )

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=KANTIAN_PROMPT,
            messages=chat_messages,
        )
    except APIError as e:
        raise RuntimeError(f"API request failed: {e}")

    reply_text = response.content[0].text
    chat_messages.append({"role": "assistant", "content": reply_text})
    return reply_text.strip(), result


def respond(message, history):
    chat_messages.append({"role": "user", "content": message})

    if message.strip().upper() == "EVALUATE":
        return evaluate(message)

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=KANTIAN_PROMPT,
            messages=chat_messages,
        )
        reply_text = response.content[0].text
        chat_messages.append({"role": "assistant", "content": reply_text})
        return reply_text.strip(), gr.skip()

    except APIError as e:
        raise RuntimeError(f"API request failed: {e}")
