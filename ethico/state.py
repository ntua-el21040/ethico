import reflex as rx
import asyncio

class State(rx.State):
    question: str = ""

    chat_history: list[tuple[str, str]] = []

    @rx.event
    def set_question(self, value: str):
        self.question = value

    @rx.event
    async def answer(self):
        answer = "This is a good question."
        self.chat_history.append((self.question, answer))
        self.question = ""
        
        yield

        for i in range(len(answer)):
            # Pause to show the streaming effect.
            await asyncio.sleep(0.1)
            # Add one letter at a time to the output.
            self.chat_history[-1] = (self.chat_history[-1][0], answer[: i + 1])
            yield