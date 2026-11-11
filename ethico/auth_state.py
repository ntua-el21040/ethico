import json
import logging
import reflex as rx

from .database import create_supabase_client


logger = logging.getLogger(__name__)


class AuthState(rx.State):
    email: str = ""
    password: str = ""

    stored_session: str = rx.LocalStorage(
        name="ethico_supabase_session",
        sync=True,
    )
    # User information for the UI
    user_id: str = ""
    user_email: str = ""

    auth_error: str = ""
    auth_loading: bool = False
    auth_checked: bool = False

    @rx.var
    def is_authenticated(self) -> bool:
        return bool(self.user_id and self.stored_session)

    @rx.event
    def set_email(self, value: str):
        self.email = value

    @rx.event
    def set_password(self, value: str):
        self.password = value

    # --------------------------
    # Internal helper methods
    # --------------------------

    def _save_session(self, session):
        """Save the latest Supabase session credentials."""
        self.stored_session = json.dumps({
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        })

        self.user_id = str(session.user.id)
        self.user_email = session.user.email or ""

    def _clear_session(self):
        self.stored_session = ""
        self.user_id = ""
        self.user_email = ""

    def _authenticated_client(self):
        """
        Create a client authenticated as the current user.

        Supabase validates the session and refreshes
        expired access tokens when necessary.
        """
        if not self.stored_session:
            raise PermissionError("Authentication required.")

        tokens = json.loads(self.stored_session)

        client = create_supabase_client()

        response = client.auth.set_session(
            tokens["access_token"],
            tokens["refresh_token"],
        )

        if not response.session:
            raise PermissionError("Invalid session.")

        # Retrieve verified identity from Supabase.
        user = client.auth.get_user().user

        if not user:
            raise PermissionError("User verification failed.")

        # Save rotated tokens, if Supabase refreshed them.
        self._save_session(response.session)

        self.user_id = str(user.id)
        self.user_email = user.email or ""

        return client

    def _restore_session(self) -> bool:
        self.user_id = ""
        self.user_email = ""

        if not self.stored_session:
            return False

        try:
            self._authenticated_client()
            return True

        except Exception:
            logger.warning(
                "Could not restore Supabase session",
                exc_info=True,
            )
            return False

    async def _reset_chat_state(self):
        """Never carry an in-memory chat across sign-in or sign-out."""
        from .state import State  # Local import avoids circular imports.

        chat_state = await self.get_state(State)
        chat_state._clear_chat()

    # --------------------------
    # Authentication events
    # --------------------------

    @rx.event
    async def sign_up(self):
        self.auth_error = ""
        self.auth_loading = True

        try:
            client = create_supabase_client()

            response = client.auth.sign_up({
                "email": self.email,
                "password": self.password,
            })

            if response.session:
                await self._reset_chat_state()
                self._save_session(response.session)
                self.auth_checked = True
                return rx.redirect("/")

            self.auth_error = (
                "Registration submitted. "
                "Check your email to confirm your account."
            )

        except Exception:
            self.auth_error = "Registration failed."

        finally:
            self.password = ""
            self.auth_loading = False

    @rx.event
    async def sign_in(self):
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

            await self._reset_chat_state()
            self._save_session(response.session)
            self.auth_checked = True
            self.password = ""

            return rx.redirect("/")

        except Exception:
            self.auth_error = "Invalid credentials or login failed."

        finally:
            self.auth_loading = False

    @rx.event
    async def restore_session(self):
        """Restore authentication when a public page loads."""
        self.auth_checked = False
        previous_user = self.user_id
        self._restore_session()
        if previous_user != self.user_id:
            await self._reset_chat_state()
        self.auth_checked = True

    @rx.event
    async def check_auth(self):
        """Protect a page using Supabase authentication."""
        self.auth_checked = False
        previous_user = self.user_id
        authenticated = self._restore_session()
        if previous_user != self.user_id:
            await self._reset_chat_state()
        self.auth_checked = True

        if not authenticated:
            return rx.redirect("/login")

    @rx.event
    async def sign_out(self):
        saved_session = self.stored_session

        # Immediately clear chat and authentication state.
        await self._reset_chat_state()
        self._clear_session()
        self.password = ""
        self.auth_checked = True

        try:
            if saved_session:
                tokens = json.loads(saved_session)
                client = create_supabase_client()

                client.auth.set_session(
                    tokens["access_token"],
                    tokens["refresh_token"],
                )

                client.auth.sign_out(
                    options={"scope": "local"}
                )

        except Exception:
            logger.warning(
                "Supabase logout request failed",
                exc_info=True,
            )

        return rx.redirect("/login")
