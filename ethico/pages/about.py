import reflex as rx
from src.text_elements import SYSTEM_INFORMATION
from ethico.components import sidebar

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
    
def about() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.center(
                about_content(),
                width="100%",
                padding="2em",
            ),
            margin_left="16em",
            width="100%",
            min_height="100dvh",
            overflow_y="auto",
        ),
        width="100%",
        align="start",
        spacing="0",
    )