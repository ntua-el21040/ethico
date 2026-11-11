import reflex as rx
from ethico.components import chat_page


def index() -> rx.Component:
    return chat_page()
