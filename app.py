import gradio as gr
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

# Configure the Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def chat(user_message, history):
    """Send a message to Gemini and return the response."""
    
    # Build the full conversation as a single prompt
    conversation = ""
    for human, assistant in history:
        conversation += f"User: {human}\nAssistant: {assistant}\n"
    conversation += f"User: {user_message}\nAssistant:"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=conversation
    )
    
    return response.text

# Build the Gradio interface
demo = gr.ChatInterface(
    fn=chat,
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