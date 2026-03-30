import os
import json
import gradio as gr
from groq import Groq
from dotenv import load_dotenv

from src.validator import CausalAgencyModel, response_schema
from src.evaluator import evaluate_dilemma
from src.prompts import SYSTEM_PROMPT2


# You must have a valid GROQ_API_KEY set in your .env file
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct" 
chat_messages = [
    {"role": "system", "content": SYSTEM_PROMPT2}
]

def analyse(message):
    """Handles the extraction of the moral dilemma into a structured JSON schema."""
    
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
            
        return reply_text
                    
    except json.JSONDecodeError:
        return "Failed to parse valid JSON."
    
    
def explain():
    """Evaluates the dilemma and generates a plain language explanation of the results."""
    evaluate_dilemma()
    try:
        with open("./data/evaluation.json", "r", encoding="utf-8") as f:
            evaluation = json.load(f)
    except FileNotFoundError:
        return "No evaluation found. Please run ANALYSE first."
            
    EXPLAIN_PROMPT = f"""The following is the output of a machine ethics evaluation of the moral dilemma we discussed.
    Each dictionary contains the permissibility of the action according to an ethical principle and the sufficient, 
    necessary and inus reasons for this evaluation. Reasons are presented in a first-order logic predicate format. 

    {json.dumps(evaluation, indent=2)}

    Explain what each result means in plain language, relate it back to the dilemma the user described."""

    # Swap out the generic EXPLAIN command with the engineered prompt
    chat_messages[-1]["content"] = EXPLAIN_PROMPT
    
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
    if command == "ANALYSE":
        return analyse(message)
    elif command == "EXPLAIN":
        return explain()
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
    description="Describe your moral dilemma. When ready, type **ANALYSE** to generate a JSON object that models the dilemma. \
                 When ready, type **EXPLAIN** to evaluate the dilemma and generate an explanation of the results.",
    examples=[
        "A doctor can save 5 patients by harvesting organs from one healthy patient. If he does, the 5 patients are saved and the healthy one dies. Else, the 5 patients die.",
    ]
)

if __name__ == "__main__":
    demo.launch(share=False)