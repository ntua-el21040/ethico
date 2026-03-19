import os
import gradio as gr
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
chat = client.chats.create(
        model="gemini-2.5-flash"
    )

def respond(user_message, history):
    """Send a message to Gemini and return the response."""
    
    response = chat.send_message(user_message)

    return response.text

# Build the Gradio interface
demo = gr.ChatInterface(
    fn=respond,
    title="Gemini Chat",
    description="A simple chat interface powered by Google Gemini",
    examples=[
        "What is utilitarianism?",
        "Explain Kant's categorical imperative",
        "What is Rawlsian justice?"
    ]
)

if __name__ == "__main__":
    demo.launch()