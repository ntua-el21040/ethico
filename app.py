import os
import json
import gradio as gr
from google import genai
from google.genai import types
from dotenv import load_dotenv

# You must have a valid GEMINI_API_KEY set in your .env file
load_dotenv()

SYSTEM_PROMPT = """You are an assistant helping users articulate moral dilemmas for analysis.

Ask clarifying questions until you understand:
1. What action the agent is considering
2. What effects the action has on others
3. Who is affected and how (positively or negatively)
4. What the agent's goal is
5. What the initial situation is. When possible, infer the initial situation or assume neutral stances.

When you have enough information, tell the user:
'I have enough information. Type ANALYSE to proceed.'

If the user types ANALYSE, respond with ONLY a valid JSON object and nothing else.
"""

response_schema = {
    "type": "object",
    "required": ["actions", "events", "utilities", "affects", "plan", "goal", "initialState"],
    "properties": {
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "intrinsicvalue", "preconditions", "effects"],
                "properties": {
                    "name": { "type": "string" },
                    "intrinsicvalue": { "type": "string", "enum": ["good", "bad", "neutral"] },
                    "preconditions": { "type": "object" },
                    "effects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["condition", "effect"],
                            "properties": {
                                "condition": { "type": "object" },
                                "effect": { "type": "object" }
                            }
                        }
                    }
                }
            }
        },
        "events": { 
            "type": "array",
            "items": { "type": "object" } 
        },
        "utilities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["fact", "utility"],
                "properties": {
                    "fact": { "type": "object" },
                    "utility": { "type": "number" }
                }
            }
        },
        "affects": { "type": "object" },
        "plan": {
            "type": "array",
            "items": { "type": "string" }
        },
        "goal": { "type": "object" },
        "initialState": { "type": "object" }
    }
}

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
chat_session = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
)

def respond(message, history):
    if message.strip().upper() == "ANALYSE":
        json_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        )
        
        response = chat_session.send_message(message, config=json_config)
        
        try:
            json_data = json.loads(response.text)
            
            file_path = "ethics_engine/cases/gemini_cases/dilemma.json" 

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)
                        
            return response.text.strip()
            
        except json.JSONDecodeError:
            return "Failed to parse valid JSON."

    response = chat_session.send_message(message)
    return response.text.strip()

demo = gr.ChatInterface(
    fn=respond,
    title="Ethics Dilemma Analyser",
    description="Describe your moral dilemma. When ready, type **ANALYSE** to generate the downloadable JSON.",
    examples=[
        "A doctor can save 5 patients by harvesting organs from one healthy patient.",
    ]
)

if __name__ == "__main__":
    demo.launch()