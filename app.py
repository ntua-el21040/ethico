import os
import json
import gradio as gr
from google import genai
from google.genai import types
from dotenv import load_dotenv
from src.validator import CausalAgencyModel
from src.prompts import SYSTEM_PROMPT

# You must have a valid GEMINI_API_KEY set in your .env file
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
chat_session = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
)

response_schema = {
    "type": "object",
    "properties": {
        "description": {
            "type": "string"
        },
        "actions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "background": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "consequences": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "mechanisms": {
            "type": "object",
            "properties": {},
        },
        "utilities": {
            "type": "object",
            "properties": {},
        },
        "intentions": {
            "type": "object",
            "properties": {},
        },
        "goals": {
            "type": "object",
            "properties": {},
        },
        "patients": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "affects": {
            "type": "object",
            "properties": {},
        }
    },
    "required": ["actions"]
}

def respond(message, history):
    if message.strip().upper() == "ANALYSE":
        json_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        )
        
        response = chat_session.send_message(message, config=json_config)
        
        try:
            json_data = json.loads(response.text)
            
            cam = CausalAgencyModel.model_validate_json(response.text)
            print(cam)
            
            file_path = "./data/situation.json" 

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)
                        
            return response.text.strip()
            
        except json.JSONDecodeError:
            return "Failed to parse valid JSON."
    
    if message.strip().upper() == "EXPLAIN":
        try:
            with open("./data/evaluation.json", "r", encoding="utf-8") as f:
                evaluation = json.load(f)
        except FileNotFoundError:
            return "No evaluation found. Please run ANALYSE first."
               
        EXPLAIN_PROMPT = f"""The following is the output of a machine ethics evaluation of the moral dilemma we discussed.
        Each key is an ethical principle and the value is whether the action is permissible according to it.

        {json.dumps(evaluation, indent=2)}

        Explain what each result means in plain language, relate it back to the dilemma the user described, and highlight the differences between the three ethical frameworks."""

        response = chat_session.send_message(EXPLAIN_PROMPT)
        return response.text.strip()

    response = chat_session.send_message(message)
    return response.text.strip()


demo = gr.ChatInterface(
    fn=respond,
    title="Ethics Dilemma Analyser",
    description="Describe your moral dilemma. When ready, type **ANALYSE** to generate the downloadable JSON. \
                 When the dilemma has been evaluated, type **EXPLAIN** to generate an explanation of the results.",
    examples=[
        "A doctor can save 5 patients by harvesting organs from one healthy patient.",
        "Bob gives Alice flowers in order to make Celia happy when she sees that Alice is thrilled about the flowers. \
        Alice being happy is not part of the goal of Bob’s action."
    ]
)

if __name__ == "__main__":
    demo.launch()