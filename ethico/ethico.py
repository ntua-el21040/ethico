import reflex as rx

from ethico import style
from ethico.state import State


def qa(question: str, answer: str) -> rx.Component:
    return rx.box(
        rx.box(rx.text(question, style=style.question_style), text_align="right"),
        rx.box(rx.text(answer, style=style.answer_style), text_align="left"),
        margin_y="1em",
        width="100%",
    )


def chat() -> rx.Component:
     return rx.box(
        rx.foreach(State.chat_history, lambda messages: qa(messages[0], messages[1]))
    )


def action_bar() -> rx.Component:
    return rx.hstack(
        rx.input(
            value=State.question,
            disabled=State.processing,
            placeholder="Ask a question",
            on_change=State.set_question,
            style=style.input_style,
        ),
        # on_click event triggers the API to send the prompt to OpenAI.
        rx.button(
            "Ask",
            on_click=State.answer,
            loading=State.processing,
            style=style.button_style,
        ),
        width="100%",
    )


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            chat(),
            action_bar(),
            rx.cond(State.error != "", rx.text(State.error, color="red", role="alert")),
            width="100%",
            max_width="48em",
            padding="1em",
            align="stretch",
        )
    )


app = rx.App()
app.add_page(index)