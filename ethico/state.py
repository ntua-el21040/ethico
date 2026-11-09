import json
import os
import asyncio
import reflex as rx
import tempfile
from pathlib import Path
from openai import APIError, AsyncOpenAI, OpenAI
from dotenv import load_dotenv

from ethico.constants import SYSTEM_PROMPT
from src.validator import Settings, UnifiedModel
from src.evaluator import evaluate_dilemma
from ethico.constants import EXPLAIN_PROMPT, tools
from rxconfig import config



MODEL = "gpt-4o-mini"
load_dotenv()

class State(rx.State):
    question: str = ""
    chat_history: list[tuple[str, str]] = []
    processing: bool = False
    error: str = ""

    @rx.event
    def set_question(self, value: str):
        self.question = value
                    
    
    @rx.event(background=True)
    async def answer(self):
        async with self:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.error = "Set OPENAI_API_KEY and restart the app."
                return
            
            question = self.question.strip()
            if not question or self.processing:
                return

            self.processing = True
            self.error = ""
            self.question = ""
            self.chat_history.append((question, ""))
        yield

        try:
            messages = self._create_message_list()
            async with AsyncOpenAI(api_key=api_key) as client:
                if question.lower() == "evaluate":
                    situation_path = await self._extract_dilemma(client, messages)
                    evaluation_path = Path(situation_path).parent / "evaluation.json"
                    evaluate_dilemma(situation_path, str(evaluation_path))
                    with open(evaluation_path, "r", encoding="utf-8") as f:
                                evaluation = json.load(f) 
                    formatted_explain_prompt = EXPLAIN_PROMPT.format(
                        evaluation=json.dumps(evaluation, indent=2)
                    )
                    
                    messages.append({
                        "role": "system",
                        "content": formatted_explain_prompt,
                    })
                                        
                
                stream = await client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    stream=True,
                )
                async with stream:
                    async for chunk in stream:
                        if not chunk.choices:
                            continue
                        text = chunk.choices[0].delta.content
                        if text:
                            async with self:
                                previous = self.chat_history[-1][1]
                                self.chat_history[-1] = (question, previous + text)
                            yield
        except APIError:
            async with self:
                self.chat_history.pop()
                self.question = question
                self.error = "The request failed. Check your API access and try again."
        finally:
            async with self:
                self.processing = False
            yield
        
            
    def _create_message_list(self) -> list[dict[str, str]]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        for previous_question, previous_answer in self.chat_history:
            messages.append({"role": "user", "content": previous_question})
            messages.append({"role": "assistant", "content": previous_answer})
        messages.append({"role": "user", "content": self.question.strip()})
        return messages
    
    
    async def _extract_dilemma(self, client: AsyncOpenAI, messages: list[dict]) -> str:
        tool = next(t for t in tools if t["name"] == "extract_dilemma")

        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[{
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                    "strict": False,
                },
            }],
            tool_choice={
                "type": "function",
                "function": {"name": "extract_dilemma"},
            },
        )

        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            raise ValueError("Failed to extract dilemma.")

        extracted_model = json.loads(tool_calls[0].function.arguments)
        UnifiedModel.model_validate(extracted_model)

        situation_path = Path(tempfile.mkdtemp(prefix="thufir_")) / "situation.json"

        with open(situation_path, "w", encoding="utf-8") as f:
            json.dump(extracted_model, f, indent=2)

        return str(situation_path)