import customtkinter as ctk

default_font_family = "Roboto"
default_font_size = 14


def get_font(family=default_font_family, size=default_font_size, weight="normal", slant="roman", underline=False):
    return ctk.CTkFont(family=family, size=size, weight=weight, slant=slant, underline=underline)


def title_font():
    """
    Preset for titles (largest).
    """
    return get_font(size=24, weight="bold")


def heading_font():
    """
    Preset for headings.
    """
    return get_font(size=18, weight="bold")


def subheading_font():
    """
    Preset for subheadings.
    """
    return get_font(size=16, weight="bold")


def body_font():
    """
    Preset for body text.
    """
    return get_font(size=14)


def button_font():
    """
    Preset for button text.
    """
    return get_font(size=12, weight="bold")


def small_font():
    """
    Preset for small text, such as captions or footnotes.
    """
    return get_font(size=12)


def micro_font():
    """
    Preset for micro text, such as version stamps.
    """
    return get_font(size=10)


def log_font():
    """
    Preset for log text.
    """
    return get_font(family="Courier", size=12)
