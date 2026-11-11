import reflex as rx
from ethico.constants import SYSTEM_INFORMATION
from ethico.components import sidebar
from ethico import style

def about_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "About THUFIR",
                **style.about_heading,
            ),
            rx.separator(),
            rx.markdown(SYSTEM_INFORMATION),
            **style.about_stack,
        ),
        **style.about_card,
    )
    
def about() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.center(
                about_content(),
                **style.about_page_center,
            ),
            **style.about_page_content,
        ),
        **style.about_page_shell,
    )