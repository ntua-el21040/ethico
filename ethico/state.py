import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path

import reflex as rx
from dotenv import load_dotenv
from openai import APIError, AsyncOpenAI

from ethico.auth_state import AuthState
from ethico.constants import EXPLAIN_PROMPT, OPENAI_TOOLS, SYSTEM_PROMPT
from ethico.conversation_service import (
    create_conversation,
    mark_evaluation_failed,
    save_evaluation,
    save_message,
    save_situation,
)
from ethico.evaluator import evaluate_dilemma
from ethico.validator import UnifiedModel


MODEL = "gpt-4o-mini"
logger = logging.getLogger(__name__)
load_dotenv()


class State(rx.State):
    question: str = ""
    chat_history: list[tuple[str, str]] = []
    processing: bool = False
    error: str = ""

    # One database conversation for the current visible chat.
    # Never restored automatically after login/restart.
    conversation_id: str = ""

    # Incremented on login/logout so an old streaming event cannot
    # write into a different user's freshly cleared chat.
    chat_generation: int = 0

    @rx.event
    def set_question(self, value: str):
        self.question = value

    def _clear_chat(self):
        """Called by AuthState on login and logout."""
        self.question = ""
        self.chat_history = []
        self.processing = False
        self.error = ""
        self.conversation_id = ""
        self.chat_generation += 1

    @rx.event(background=True)
    async def answer(self):
        async with self:
            question = self.question.strip()
            if not question or self.processing:
                return

            # Authorization is enforced in the backend event itself.
            auth = await self.get_state(AuthState)
            try:
                supabase = auth._authenticated_client()
                user_id = auth.user_id  # Derived from Supabase get_user().
            except Exception:
                logger.warning("Rejected unauthenticated chat event", exc_info=True)
                self.error = "Please log in before using the chat."
                return

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.error = "Set OPENAI_API_KEY and restart the app."
                return

            self.processing = True
            self.error = ""
            self.question = ""
            self.chat_history.append((question, ""))
            messages = self._create_message_list()
            conversation_id = self.conversation_id
            generation = self.chat_generation
        yield

        user_saved = False
        assistant_saved = False
        answer_parts: list[str] = []

        try:
            # The first sent message starts a new DB conversation.
            if not conversation_id:
                conversation_id = await asyncio.to_thread(
                    create_conversation, supabase, user_id, question[:80]
                )
                async with self:
                    if self.chat_generation != generation:
                        return
                    self.conversation_id = conversation_id
                yield

            async with self:
                if self.chat_generation != generation:
                    return

            # Persist before calling OpenAI, so a failed generation
            # does not lose the user's submitted message.
            await asyncio.to_thread(
                save_message, supabase, conversation_id, "user", question
            )
            user_saved = True

            async with AsyncOpenAI(api_key=api_key) as openai:
                if question.lower() == "evaluate":
                    situation_path = await self._extract_dilemma(openai, messages)
                    evaluation_path = Path(situation_path).parent / "evaluation.json"

                    with open(situation_path, encoding="utf-8") as f:
                        situation = json.load(f)

                    # Save situation.json NOW, before HERA starts.
                    # Each evaluate command creates a fresh run.
                    run_id = await asyncio.to_thread(
                        save_situation, supabase, conversation_id, situation
                    )

                    try:
                        # HERA is synchronous; avoid blocking the event loop.
                        await asyncio.to_thread(
                            evaluate_dilemma,
                            situation_path,
                            str(evaluation_path),
                        )
                        with open(evaluation_path, encoding="utf-8") as f:
                            evaluation = json.load(f)
                    except Exception as exc:
                        try:
                            await asyncio.to_thread(
                                mark_evaluation_failed,
                                supabase,
                                run_id,
                                f"{type(exc).__name__}: {exc}",
                            )
                        except Exception:
                            logger.exception("Could not mark evaluation run as failed")
                        raise

                    await asyncio.to_thread(
                        save_evaluation, supabase, run_id, evaluation
                    )
                    messages.append({
                        "role": "system",
                        "content": EXPLAIN_PROMPT.format(
                            evaluation=json.dumps(evaluation, indent=2)
                        ),
                    })

                stream = await openai.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    stream=True,
                )
                async with stream:
                    async for chunk in stream:
                        if not chunk.choices:
                            continue
                        delta = chunk.choices[0].delta.content
                        if not delta:
                            continue

                        async with self:
                            if self.chat_generation != generation:
                                # User logged out or started a new chat.
                                return
                            previous = self.chat_history[-1][1]
                            self.chat_history[-1] = (question, previous + delta)
                        answer_parts.append(delta)
                        yield

            async with self:
                if self.chat_generation != generation:
                    return

            # Store one assistant message after the streamed answer completes.
            if answer_parts:
                await asyncio.to_thread(
                    save_message,
                    supabase,
                    conversation_id,
                    "assistant",
                    "".join(answer_parts),
                )
                assistant_saved = True

        except APIError:
            logger.exception("OpenAI request failed")
            async with self:
                if self.chat_generation == generation:
                    self.error = "The request failed. Check your API access and try again."
        except Exception:
            logger.exception("Chat processing or persistence failed")
            async with self:
                if self.chat_generation == generation:
                    self.error = "Could not process or save this message. Check the server logs."
                    if not user_saved:
                        # Do not display a message that was never saved.
                        self.chat_history.pop()
                        self.question = question
        finally:
            # If streaming failed halfway, retain the partial assistant answer.
            if user_saved and answer_parts and not assistant_saved:
                async with self:
                    same_chat = self.chat_generation == generation
                if same_chat:
                    try:
                        await asyncio.to_thread(
                            save_message,
                            supabase,
                            conversation_id,
                            "assistant",
                            "".join(answer_parts),
                        )
                    except Exception:
                        logger.exception("Could not save partial assistant reply")

            async with self:
                if self.chat_generation == generation:
                    self.processing = False
            yield

    def _create_message_list(self) -> list[dict[str, str]]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for previous_question, previous_answer in self.chat_history:
            messages.append({"role": "user", "content": previous_question})
            if previous_answer:
                messages.append({"role": "assistant", "content": previous_answer})
        return messages

    async def _extract_dilemma(
        self, client: AsyncOpenAI, messages: list[dict]
    ) -> str:
        tool = next(
            t for t in OPENAI_TOOLS
            if t["function"]["name"] == "extract_dilemma"
        )

        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[tool],
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
