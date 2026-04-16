import os
import json
import gradio as gr
from groq import Groq
from dotenv import load_dotenv

from src.validator import CausalAgencyModel, response_schema
from src.evaluator import evaluate_dilemma
from text_elements import SYSTEM_PROMPT, EXPLAIN_PROMPT


# You must have a valid GROQ_API_KEY set in your .env file
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct" 
chat_messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def evaluate(message):
    """Handles extraction, evaluation, and explanation in a single step."""
    
    # Step 1: Extract JSON
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=chat_messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "dilemma_analysis",
                "schema": response_schema
            }
        }
    )
    
    reply_text = response.choices[0].message.content
    chat_messages.append({"role": "assistant", "content": reply_text})
    
    try:
        json_data = json.loads(reply_text)
        CausalAgencyModel.model_validate_json(reply_text)
        
        file_path = "./data/situation.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
            
    except json.JSONDecodeError:
        return "Failed to parse valid JSON."

    # Step 2: Evaluate and explain
    evaluate_dilemma()
    try:
        with open("./data/evaluation.json", "r", encoding="utf-8") as f:
            evaluation = json.load(f)
    except FileNotFoundError:
        return "Evaluation failed. Please try again."
    
    EXPLAIN_PROMPT.format(evaluation=json.dumps(evaluation, indent=2))
    chat_messages.append({"role": "user", "content": EXPLAIN_PROMPT})
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=chat_messages
    )
    
    reply_text = response.choices[0].message.content
    chat_messages.append({"role": "assistant", "content": reply_text})
    return reply_text.strip()


def respond(message, history):
    chat_messages.append({"role": "user", "content": message})
    
    command = message.strip().upper()
    if command == "EVALUATE":
        return evaluate(message)
    else:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=chat_messages
        )
        
        reply_text = response.choices[0].message.content
        chat_messages.append({"role": "assistant", "content": reply_text})
        return reply_text.strip()


demo = gr.ChatInterface(
    fn=respond,
    title="Ethics Dilemma Analyser",
    description="Describe your moral dilemma. When ready, type **EVALUATE** to analyse and explain the dilemma.",
    examples=[
        "A doctor can save 5 patients by harvesting organs from one healthy man. If he does, the 5 patients are saved and the healthy one dies. Else, the 5 patients die.",
        "Ένας γιατρός μπορεί να σώσει 5 ασθενείς αφαιρώντας όργανα από έναν υγιή άνθρωπο. Αν το κάνει, οι 5 ασθενείς σώζονται και ο υγιής πεθαίνει. Διαφορετικά, οι 5 ασθενείς πεθαίνουν."
    ]
)

if __name__ == "__main__":
    demo.launch(share=False)