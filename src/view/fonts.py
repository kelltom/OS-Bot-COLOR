import customtkinter as ctk

default_font_family = "Arial"
default_font_size = 14

def default_font(family=default_font_family, size=default_font_size):
    return ctk.CTkFont(family=family, size=size)

def title_font():
    """
    Preset for titles (largest).
    """
    return default_font(size=24) # TODO: BOLD

def heading_font():
    """
    Preset for headings.
    """
    return default_font(size=18) # TODO: BOLD

def subheading_font():
    """
    Preset for subheadings.
    """
    return default_font(size=16) # TODO: BOLD

def body_font():
    """
    Preset for body text.
    """
    return default_font(size=14)

def button_font():
    """
    Preset for button text.
    """
    return default_font(size=12) # TODO: BOLD

def small_font():
    """
    Preset for small text, such as captions or footnotes.
    """
    return default_font(size=12)

def micro_font():
    """
    Preset for micro text, such as version stamps.
    """
    return default_font(size=10)

def log_font():
    """
    Preset for log text.
    """
    return default_font(family="Courier", size=12)  # Monospace font often used for logs
