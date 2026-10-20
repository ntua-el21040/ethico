import json
import gradio as gr
import shutil
import tempfile
import os
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

def evaluate(messages):
    print(messages)
    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=UNIFIED_PROMPT,
            messages=messages,
            tools=tools,
            tool_choice={"type": "tool", "name": "extract_dilemma"},
        )
    except APIError:
        raise gr.Error("The model failed to extract the dilemma. Please try again.")

    tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
    if not tool_use_blocks:
        raise gr.Error("The model failed to trigger the required tool. Please try again.")

    first_tool_block = tool_use_blocks[0]
    extracted_model = first_tool_block.input

    try:
        UnifiedModel.model_validate(extracted_model)
    except Exception:
        raise gr.Error("There was an error creating the dilemma. Please ensure your input is well-formed and try again.")

    tmp_dir = tempfile.mkdtemp(prefix="thufir_")
    situation_path = os.path.join(tmp_dir, "situation.json")
    evaluation_path = os.path.join(tmp_dir, "evaluation.json")

    with open(situation_path, "w", encoding="utf-8") as f:
        json.dump(extracted_model, f, indent=2)

    try:
        evaluate_dilemma(situation_path, evaluation_path)
        with open(evaluation_path, "r", encoding="utf-8") as f:
            evaluation = json.load(f)
    except Exception:
        raise gr.Error("The ethics engine could not evaluate this dilemma. Please ensure your input is well-formed and try again.")

    formatted_explain_prompt = EXPLAIN_PROMPT.format(
        evaluation=json.dumps(evaluation, indent=2)
    )

    tool_results = []
    for block in tool_use_blocks:
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": formatted_explain_prompt if block.id == first_tool_block.id
                       else "Ignored. Evaluated the first dilemma successfully.",
        })

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=UNIFIED_PROMPT,
            messages=messages,
            tools=tools,
        )
    except APIError:
        raise gr.Error("There was an error handling the evaluation. Please try again.")

    reply_text = next((b.text for b in response.content if b.type == "text"), "")
    return reply_text.strip(), extracted_model


def respond(message, history):
    if not message or not message.strip():
        return "Please provide a non-empty message.", gr.skip()
    
    messages = [{"role": t["role"], "content": t["content"]} for t in history]
    messages.append({"role": "user", "content": message})
    if message.strip().upper() == "EVALUATE":
        return evaluate(messages)

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=UNIFIED_PROMPT,
            messages=messages,
        )
        reply = response.content[0].text
        return reply.strip(), gr.skip()

    except APIError as e:
        print(f"API request failed: {e}")
        raise RuntimeError(f"API request failed: {e}")
