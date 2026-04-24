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
        raise gr.Error(f"The model failed to extract the dilemma. Please try again.")

    tool_use_block = response.content[0]
    if not tool_use_block:
        raise gr.Error(
            "The model failed to trigger the required tool. Please try again."
        )

    tool_use_id = tool_use_block.id
    extracted_model = tool_use_block.input

    try:
        KantianModel.model_validate(extracted_model)
    except Exception:
        raise gr.Error(
            "There was an error creating the dilemma. Please ensure your input is well-formed and try again."
        )

    try:
        file_path = "./data/situation.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(extracted_model, f, indent=2)
    except OSError:
        raise gr.Error("Failed to save the dilemma. Check file permissions.")

    try:
        evaluate_dilemma()
    except Exception:
        raise gr.Error(
            "The ethics engine could not evaluate this dilemma. Please ensure your input is well-formed and try again."
        )

    try:
        with open("./data/evaluation.json", "r", encoding="utf-8") as f:
            evaluation = json.load(f)
    except Exception:
        raise gr.Error(
            "There was an error loading the evaluation results. Please try again."
        )

    formatted_explain_prompt = EXPLAIN_PROMPT.format(
        evaluation=json.dumps(evaluation, indent=2)
    )

    chat_messages.append({"role": "assistant", "content": response.content})
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
            tools=tools,
        )
    except APIError:
        raise gr.Error("There was an error handling the evaluation. Please try again.")

    reply_text = next(
        (block.text for block in response.content if block.type == "text"), ""
    )

    chat_messages.append({"role": "assistant", "content": reply_text})
    return reply_text.strip(), extracted_model


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
