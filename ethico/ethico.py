import reflex as rx

from ethico.auth_state import AuthState
from ethico.pages.dilemmas import dilemmas
from ethico.pages.login import login
from ethico.pages.about import about
from ethico.pages.index import index
    
   
app = rx.App()
app.add_page(
    login,
    route="/login",
    on_load=AuthState.restore_session,
)
app.add_page(index, route="/", title="THUFIR")
app.add_page(about, route="/about", title="About THUFIR")
app.add_page(
    dilemmas,
    route="/dilemmas",
    on_load=AuthState.check_auth,
)