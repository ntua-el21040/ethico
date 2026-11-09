import os
import asyncio
import reflex as rx
from openai import APIError, AsyncOpenAI
from dotenv import load_dotenv
from ethico.constants import SYSTEM_PROMPT


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
            question = self.question.strip()
            if not question or self.processing:
                return

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.error = "Set OPENAI_API_KEY and restart the app."
                return

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            
            for previous_question, previous_answer in self.chat_history:
                messages.append({"role": "user", "content": previous_question})
                messages.append({"role": "assistant", "content": previous_answer})
            messages.append({"role": "user", "content": question})

            self.processing = True
            self.error = ""
            self.question = ""
            self.chat_history.append((question, ""))
        yield

        try:
            async with AsyncOpenAI(api_key=api_key) as client:
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