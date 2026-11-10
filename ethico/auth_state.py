import reflex as rx
import logging

from .database import create_supabase_client

logger = logging.getLogger(__name__)

class AuthState(rx.State):
    email: str = ""
    password: str = ""

    user_id: str = ""
    user_email: str = ""
    access_token: str = ""
    refresh_token: str = ""

    auth_error: str = ""
    auth_loading: bool = False

    @rx.event
    def set_email(self, value: str):
        self.email = value

    @rx.event
    def set_password(self, value: str):
        self.password = value

    @rx.var
    def is_authenticated(self) -> bool:
        return bool(self.user_id and self.access_token)

    @rx.event
    def sign_up(self):
        self.auth_error = ""
        self.auth_loading = True

        try:
            client = create_supabase_client()

            response = client.auth.sign_up({
                "email": self.email,
                "password": self.password,
            })

            if response.session:
                self._save_session(response.session)
                return rx.redirect("/")

            self.auth_error = (
                "Registration submitted. Check your email "
                "to confirm your account."
            )

        except Exception:
            self.auth_error = "Registration failed."

        finally:
            self.auth_loading = False

    @rx.event
    def sign_in(self):
        self.auth_error = ""
        self.auth_loading = True

        try:
            client = create_supabase_client()

            response = client.auth.sign_in_with_password({
                "email": self.email,
                "password": self.password,
            })

            if not response.session:
                self.auth_error = "Login failed."
                return

            self._save_session(response.session)
            self.password = ""

            return rx.redirect("/")

        except Exception:
            self.auth_error = "Invalid credentials or login failed."

        finally:
            self.auth_loading = False

    def _save_session(self, session):
        self.access_token = session.access_token
        self.refresh_token = session.refresh_token
        self.user_id = session.user.id
        self.user_email = session.user.email or ""

    @rx.event
    def sign_out(self):
        # Preserve tokens temporarily for Supabase logout.
        access_token = self.access_token
        refresh_token = self.refresh_token

        # Immediately clear the local authentication state.
        self.reset()

        try:
            if access_token and refresh_token:
                client = create_supabase_client()

                # Restore the session on this temporary client.
                client.auth.set_session(
                    access_token,
                    refresh_token,
                )

                # Revoke the current session's refresh token.
                client.auth.sign_out(
                    options={"scope": "local"}
                )

        except Exception:
            logger.exception("Supabase sign-out failed")

        return rx.redirect("/")