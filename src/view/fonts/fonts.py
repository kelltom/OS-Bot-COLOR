import customtkinter as ctk

default_font_family = "Trebuchet MS"
default_font_size = 14


def get_font(family=default_font_family, size=default_font_size, weight="normal", slant="roman", underline=False):
    return ctk.CTkFont(family=family, size=size, weight=weight, slant=slant, underline=underline)


def title_font():
    """
    Preset for titles (largest).
    """
    return get_font(size=24, weight="bold")


def heading_font(size=18):
    """
    Preset for headings.
    """
    return get_font(size=size, weight="bold")


def subheading_font(size=16):
    """
    Preset for subheadings.
    """
    return get_font(size=size, weight="bold")


def body_large_font(size=15):
    """
    Preset for body text.
    """
    return get_font(size=size)


def body_med_font(size=14):
    """
    Preset for body text.
    """
    return get_font(size=size)


def button_med_font(size=14):
    """
    Preset for button text.
    """
    return get_font(size=size, weight="bold")


def button_small_font(size=12):
    """
    Preset for button text.
    """
    return get_font(size=size, weight="bold")


def small_font(size=12):
    """
    Preset for small text, such as captions or footnotes.
    """
    return get_font(size=size)


def micro_font(size=10):
    """
    Preset for micro text, such as version stamps.
    """
    return get_font(size=size)


def log_font(size=12):
    """
    Preset for log text.
    """
    return get_font(family="Cascadia Code", size=size)
