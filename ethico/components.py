import reflex as rx 

from ethico import style
from ethico.state import State
from ethico.constants import INTRO_MESSAGE
from ethico.auth_state import AuthState

def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, **style.sidebar_link_text),
            **style.sidebar_link_row,
        ),
        href=href,
        **style.sidebar_link_style,
    )



def sidebar_items() -> rx.Component:
    return rx.vstack(
        sidebar_item("Chat", "message_circle", "/"),
        sidebar_item("Dilemmas", "scale", "/#"),
        sidebar_item("About", "info", "/about"),
        **style.sidebar_navigation,
    )



def sidebar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.image(
                src="https://web.reflex-assets.dev/other/logo.jpg",
                alt="THUFIR Logo",
                **style.sidebar_logo,
            ),
            rx.heading(
                "THUFIR",
                **style.sidebar_heading,
            ),
            **style.sidebar_brand_row,
        ),

        sidebar_items(),
        rx.spacer(),

        rx.vstack(
            # Show logout when authenticated,
            # otherwise show login.
            rx.cond(
                AuthState.is_authenticated,
                rx.button(
                    rx.icon("log-out"),
                    rx.text("Log out", size="4"),
                    on_click=AuthState.sign_out,
                    **style.sidebar_logout,
                ),
                sidebar_item(
                    "Log in",
                    "log-in",
                    "/login",
                ),
            ),

            rx.divider(),

            # Account information is only visible
            # when the user is authenticated.
            rx.cond(
                AuthState.is_authenticated,
                rx.hstack(
                    rx.icon(
                        "user",
                        size=24,
                    ),
                    rx.vstack(
                        rx.text(
                            "My account",
                            **style.sidebar_account_title,
                        ),
                        rx.text(
                            AuthState.user_email,
                            **style.sidebar_account_email,
                        ),
                        **style.sidebar_account_info,
                    ),
                    **style.sidebar_account_row,
                ),
            ),

            **style.sidebar_footer,
        ),

        **style.sidebar_container,
    )

def qa(question: str, answer: str) -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.markdown(question),
            **style.question_style,
        ),
        rx.box(
            rx.markdown(answer),
            **style.answer_style,
        ),
        **style.message_stack,
    )

def chat() -> rx.Component:
    return rx.box(
        rx.auto_scroll(
            rx.cond(
                State.chat_history.length() == 0, # type: ignore
                rx.box(
                    rx.markdown(INTRO_MESSAGE),
                    **style.intro_message,
                ),
            ),
            rx.foreach(
                State.chat_history,
                lambda messages: qa(messages[0], messages[1]),
            ),
            **style.chat_scroll,
        ),
        **style.chat_panel,
    )
    

def action_bar() -> rx.Component:
    enabled = AuthState.auth_checked & AuthState.is_authenticated
    return rx.vstack(
        rx.hstack(
            rx.input(
                value=State.question,
                disabled=State.processing | ~enabled,
                placeholder="Ask a question",
                on_change=State.set_question,
                style=style.input_style,
            ),
            rx.button(
                "Ask",
                on_click=State.answer,
                disabled=~enabled,
                loading=State.processing,
                style=style.button_style,
            ),
            **style.action_bar_row,
        ),
        rx.cond(
            State.error != "",
            rx.text(State.error, **style.error_text),
        ),
        **style.action_bar_container,
    )


def chat_page() -> rx.Component:
    """Shared layout for the main chat and dilemmas pages."""
    return rx.hstack(
        sidebar(),
        rx.center(
            rx.vstack(
                chat(),
                action_bar(),
                rx.cond(
                    State.error != "",
                    rx.text(State.error, role="alert", **style.error_text),
                ),
                **style.chat_column,
            ),
            **style.page_content,
        ),
        **style.page_shell,
    )
