import reflex as rx
from ethico.components import sidebar, action_bar, chat
from ethico.state import State

def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.center(
            rx.vstack(
                chat(),
                action_bar(),
                rx.cond(
                    State.error != "",
                    rx.text(State.error, color="red", role="alert"),
                ),
                width="100%",
                max_width="48em",
                height="100%",
                min_height="0",
                padding="1em",
                spacing="3",
                align="stretch",
            ),
            flex="1",
            min_width="0",
            margin_left="16em",
            height="100dvh",
            overflow="hidden",
        ),
        width="100%",
        height="100dvh",
        spacing="0",
        align="stretch",
        overflow="hidden",
    )