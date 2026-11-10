
import reflex as rx
from ..auth_state import AuthState


def login_page():
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Ethico", size="7"),
                rx.text("Sign in to your account"),

                rx.input(
                    placeholder="Email",
                    type="email",
                    value=AuthState.email,
                    on_change=AuthState.set_email,
                    width="100%",
                ),

                rx.input(
                    placeholder="Password",
                    type="password",
                    value=AuthState.password,
                    on_change=AuthState.set_password,
                    width="100%",
                ),

                rx.cond(
                    AuthState.auth_error != "",
                    rx.text(
                        AuthState.auth_error,
                        color="red",
                    ),
                ),

                rx.button(
                    "Sign in",
                    on_click=AuthState.sign_in,
                    loading=AuthState.auth_loading,
                    width="100%",
                ),

                rx.button(
                    "Create account",
                    on_click=AuthState.sign_up,
                    variant="outline",
                    width="100%",
                ),

                spacing="4",
                width="300px",
            ),
        ),
        height="100vh",
    )
