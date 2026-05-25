import json
import gradio as gr
from anthropic import Anthropic, APIError
from src.evaluator import evaluate_dilemma
from src.validator import (
    Settings,
    UnifiedModel,
)
from src.text_elements import (
    UNIFIED_PROMPT,
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
            system=UNIFIED_PROMPT,
            messages=chat_messages,
            tools=tools,
            tool_choice={"type": "tool", "name": "extract_dilemma"},
        )
    except APIError as e:
        raise gr.Error(f"The model failed to extract the dilemma. Please try again.")

    tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

    if not tool_use_blocks:
        raise gr.Error(
            "The model failed to trigger the required tool. Please try again."
        )

    first_tool_block = tool_use_blocks[0]
    tool_use_id = first_tool_block.id
    extracted_model = first_tool_block.input

    try:
        UnifiedModel.model_validate(extracted_model)
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

    # Multiple tool use calls may be present due to Anthropic conventions.
    # Only the successful one is used, but all must be present. 
    tool_results = []
    for block in tool_use_blocks:
        if block.id == tool_use_id:
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": formatted_explain_prompt,
            })
        else:
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": "Ignored. Evaluated the first dilemma successfully.",
            })

    chat_messages.append({"role": "assistant", "content": response.content})
    
    chat_messages.append(
        {
            "role": "user",
            "content": tool_results,
        }
    )

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=UNIFIED_PROMPT,
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
            system=UNIFIED_PROMPT,
            messages=chat_messages,
        )
        reply_text = response.content[0].text
        chat_messages.append({"role": "assistant", "content": reply_text})
        return reply_text.strip(), gr.skip()

    except APIError as e:
        raise RuntimeError(f"API request failed: {e}")
