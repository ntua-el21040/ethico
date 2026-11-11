import reflex as rx
from ..auth_state import AuthState
from ethico import style


def login():
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Ethico", **style.login_heading),
                rx.text("Sign in to your account"),

                rx.input(
                    placeholder="Email",
                    type="email",
                    value=AuthState.email,
                    on_change=AuthState.set_email,
                    **style.login_input,
                ),

                rx.input(
                    placeholder="Password",
                    type="password",
                    value=AuthState.password,
                    on_change=AuthState.set_password,
                    **style.login_input,
                ),

                rx.cond(
                    AuthState.auth_error != "",
                    rx.text(
                        AuthState.auth_error,
                        **style.login_error,
                    ),
                ),

                rx.button(
                    "Sign in",
                    on_click=AuthState.sign_in,
                    loading=AuthState.auth_loading,
                    **style.login_button,
                ),

                rx.button(
                    "Create account",
                    on_click=AuthState.sign_up,
                    **style.login_secondary_button,
                ),

                **style.login_stack,
            ),
        ),
        **style.login_page,
    )
