import reflex as rx
from ethico import style
from ethico.state import State
from ethico.constants import INTRO_MESSAGE, SYSTEM_INFORMATION

def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "bg": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
                "border-radius": "0.5em",
            },
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
    )



def sidebar_items() -> rx.Component:
    return rx.vstack(
        sidebar_item("Chat", "message_circle", "/"),
        sidebar_item("Dilemmas", "scale", "/#"),
        sidebar_item("About", "info", "/about"),
        spacing="1",
        width="100%",
    )


def sidebar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.image(
                src="https://web.reflex-assets.dev/other/logo.jpg",
                alt="THUFIR Logo",
                width="2.25em",
                height="auto",
                border_radius="25%",
            ),
            rx.heading("THUFIR", as_="h2", size="7", weight="bold"),
            align="center",
            justify="start",
            padding_x="0.5rem",
            width="100%",
        ),
        sidebar_items(),
        rx.spacer(),
        rx.vstack(
            rx.vstack(
                sidebar_item("Settings", "settings", "/#"),
                sidebar_item("Log out", "log-out", "/#"),
                spacing="1",
                width="100%",
            ),
            rx.divider(),
            rx.hstack(
                rx.icon_button(
                    rx.icon("user"), size="3", radius="full"
                ),
                rx.vstack(
                    rx.box(
                        rx.text("My account", size="3", weight="bold"),
                        rx.text(
                            "user@reflex.dev", size="2", weight="medium"
                        ),
                        width="100%",
                    ),
                    spacing="0",
                    align="start",
                    justify="start",
                    width="100%",
                ),
                padding_x="0.5rem",
                align="center",
                justify="start",
                width="100%",
            ),
            width="100%",
            spacing="5",
        ),
        spacing="5",
        padding_x="1em",
        padding_y="1.5em",
        bg=rx.color("accent", 3),
        align="start",
        position="fixed",
        top="0",
        left="0",
        height="100dvh",
        width="16em",
        overflow_y="auto",
        z_index="10",
    )
    
def qa(question: str, answer: str) -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.markdown(question),
            bg=rx.color("accent", 3),
            border="1px solid",
            border_color=rx.color("accent", 5),
            padding="1em",
            border_radius="12px",
            align_self="end",
            max_width="85%",
            overflow_wrap="anywhere",
        ),
        rx.box(
            rx.markdown(answer),
            bg=rx.color("slate", 4),
            border="1px solid",
            border_color=rx.color("slate", 6),
            padding="1em",
            border_radius="12px",
            align_self="start",
            max_width="85%",
            overflow_wrap="anywhere",
        ),
        width="100%",
        spacing="3",
        align="stretch",
        margin_y="0.5em",
    )

def chat() -> rx.Component:
    return rx.box(
        rx.auto_scroll(
            rx.cond(
                State.chat_history.length() == 0,
                rx.box(
                    rx.markdown(INTRO_MESSAGE),
                    padding="1em",
                    bg=rx.color("slate", 4),
                    border_radius="12px",
                    align_self="start",
                    max_width="85%",
                ),
            ),
            rx.foreach(
                State.chat_history,
                lambda messages: qa(messages[0], messages[1]),
            ),
            width="100%",
            height="100%",
            min_height="0",
            padding="1em",
        ),
        width="100%",
        flex="1",
        min_height="0",
        bg=rx.color("slate", 1),
        border="1px solid",
        border_color=rx.color("slate", 6),
        border_radius="16px",
        box_shadow="0 2px 12px rgba(0, 0, 0, 0.05)",
        overflow="hidden",
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
        rx.button(
            "Ask",
            on_click=State.answer,
            loading=State.processing,
            style=style.button_style,
        ),
        width="100%",
    )


def about_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "About THUFIR",
                size="8",
                weight="bold",
            ),
            rx.separator(),
            rx.markdown(SYSTEM_INFORMATION),
            spacing="5",
            align="stretch",
            width="100%",
        ),
        width="100%",
        max_width="52em",
        padding="2em",
        bg=rx.color("slate", 1),
        border="1px solid",
        border_color=rx.color("slate", 6),
        border_radius="16px",
    )