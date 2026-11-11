"""Centralized visual tokens and component/page styles for Ethico."""
import reflex as rx

# Design tokens: change these to adjust the application consistently.
SIDEBAR_WIDTH = "16em"
CHAT_MAX_WIDTH = "48em"
CONTENT_MAX_WIDTH = "52em"
MESSAGE_MAX_WIDTH = "85%"
RADIUS_SMALL = "0.5em"
RADIUS_MESSAGE = "12px"
RADIUS_PANEL = "16px"
CONTROL_HEIGHT = "44px"

ACCENT = "accent"
NEUTRAL = "slate"

# Shared layout primitives
page_shell = dict(width="100%", height="100dvh", spacing="0", align="stretch", overflow="hidden")
page_content = dict(flex="1", min_width="0", margin_left=SIDEBAR_WIDTH, height="100dvh", overflow="hidden")
chat_column = dict(width="100%", max_width=CHAT_MAX_WIDTH, height="100%", min_height="0", padding="1em", spacing="3", align="stretch")
error_text = dict(color=rx.color("red", 11), size="2")

# Sidebar
sidebar_container = dict(
    spacing="5", padding_x="1em", padding_y="1.5em", bg=rx.color(ACCENT, 3),
    align="start", position="fixed", top="0", left="0", height="100dvh",
    width=SIDEBAR_WIDTH, overflow_y="auto", z_index="10",
)
sidebar_brand_row = dict(align="center", justify="start", padding_x="0.5rem", width="100%")
sidebar_logo = dict(width="2.25em", height="auto", border_radius="25%")
sidebar_heading = dict(as_="h2", size="7", weight="bold")
sidebar_navigation = dict(spacing="1", width="100%")
sidebar_link_style = dict(underline="none", weight="medium", width="100%")
sidebar_link_row = dict(
    width="100%", padding_x="0.5rem", padding_y="0.75rem", align="center",
    style={"_hover": {"bg": rx.color(ACCENT, 4), "color": rx.color(ACCENT, 11)}, "border_radius": RADIUS_SMALL},
)
sidebar_link_text = dict(size="4")
sidebar_footer = dict(width="100%", spacing="4")
sidebar_logout = dict(variant="ghost", width="100%", justify="start")
sidebar_account_row = dict(padding_x="0.5rem", align="center", justify="start", width="100%")
sidebar_account_info = dict(spacing="0", align="start", width="100%")
sidebar_account_title = dict(size="3", weight="bold")
sidebar_account_email = dict(size="2", weight="medium", overflow_wrap="anywhere")

# Chat
message_stack = dict(width="100%", spacing="3", align="stretch", margin_y="0.5em")
message_base = dict(padding="1em", border="1px solid", border_radius=RADIUS_MESSAGE,
                    max_width=MESSAGE_MAX_WIDTH, overflow_wrap="anywhere")
question_style = message_base | dict(bg=rx.color(ACCENT, 3), border_color=rx.color(ACCENT, 5), align_self="end")
answer_style = message_base | dict(bg=rx.color(NEUTRAL, 4), border_color=rx.color(NEUTRAL, 6), align_self="start")
intro_message = dict(padding="1em", bg=rx.color(NEUTRAL, 4), border_radius=RADIUS_MESSAGE,
                     align_self="start", max_width=MESSAGE_MAX_WIDTH)
chat_panel = dict(width="100%", flex="1", min_height="0", bg=rx.color(NEUTRAL, 1),
                  border="1px solid", border_color=rx.color(NEUTRAL, 6),
                  border_radius=RADIUS_PANEL, box_shadow="0 2px 12px rgba(0, 0, 0, 0.05)", overflow="hidden")
chat_scroll = dict(width="100%", height="100%", min_height="0", padding="1em")
action_bar_container = dict(width="100%", spacing="2")
action_bar_row = dict(width="100%")
input_style = dict(
    width="100%", min_width="0", flex="1", height=CONTROL_HEIGHT,
    border_radius=RADIUS_MESSAGE, background_color=rx.color(NEUTRAL, 1),
    border=f"1px solid {rx.color(NEUTRAL, 7)}", box_shadow="none",
    **{
        "& input": {"padding": "0 14px", "font_size": "14px", "border": "none", "outline": "none", "box_shadow": "none", "background": "transparent"},
        "& input::placeholder": {"color": rx.color(NEUTRAL, 11)},
        "&:focus-within": {"border_color": rx.color(ACCENT, 8), "box_shadow": f"0 0 0 3px {rx.color(ACCENT, 3)}"},
    },
)
button_style = dict(
    flex_shrink="0", height=CONTROL_HEIGHT, padding="0 20px", border_radius=RADIUS_MESSAGE,
    font_weight="600", background_color=rx.color(ACCENT, 9), color="white", cursor="pointer",
    _hover={"background_color": rx.color(ACCENT, 10)},
    _disabled={"opacity": "0.65", "cursor": "not-allowed"},
)

# About
about_page_content = dict(margin_left=SIDEBAR_WIDTH, width="100%", min_height="100dvh", overflow_y="auto")
about_page_center = dict(width="100%", padding="2em")
about_page_shell = dict(width="100%", align="start", spacing="0")
about_card = dict(width="100%", max_width=CONTENT_MAX_WIDTH, padding="2em", bg=rx.color(NEUTRAL, 1),
                  border="1px solid", border_color=rx.color(NEUTRAL, 6), border_radius=RADIUS_PANEL)
about_stack = dict(spacing="5", align="stretch", width="100%")
about_heading = dict(size="8", weight="bold")

# Login
login_page = dict(height="100vh")
login_stack = dict(spacing="4", width="300px")
login_heading = dict(size="7")
login_input = dict(width="100%")
login_button = dict(width="100%")
login_secondary_button = dict(variant="outline", width="100%")
login_error = dict(color="red")
