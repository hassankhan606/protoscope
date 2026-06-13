"""
BioDiscover Color Theme - Bright Modern Biotech
Light-first palette with teal/blue accents and dark navy navbar.
"""


class BioTheme:
    # Navbar (always dark)
    NAV_BG        = "#0a1628"
    NAV_ACCENT    = "#00d4aa"
    NAV_TEXT      = "#8ca0b8"
    NAV_ACTIVE_BG = "#0d2b24"   # dark teal tint (no alpha needed)

    # App backgrounds (bright)
    BG_MAIN   = "#f8f9fc"   # Page background
    BG_PANEL  = "#ffffff"   # Cards, panels
    BG_CARD   = "#f1f4f9"   # Secondary cards
    BG_DARK   = "#0a1628"   # Molecule viewer bg

    # Accents
    ACCENT_TEAL   = "#00d4aa"
    ACCENT_BLUE   = "#2563eb"
    ACCENT_PURPLE = "#7c3aed"
    ACCENT_AMBER  = "#d97706"
    ACCENT_RED    = "#dc2626"

    # Text
    TEXT_MAIN    = "#0f172a"
    TEXT_SUB     = "#475569"
    TEXT_DIM     = "#94a3b8"
    TEXT_FAINT   = "#cbd5e1"

    # Borders
    BORDER       = "#e2e8f0"
    BORDER_MED   = "#cbd5e1"

    # Section label color
    SECTION_LABEL = "#00d4aa"

    # Tag presets
    TAG_TEAL   = ("#e1f5ee", "#0f6e56", "#9fe1cb")   # bg, fg, border
    TAG_BLUE   = ("#e6f1fb", "#185fa5", "#b5d4f4")
    TAG_AMBER  = ("#faeeda", "#854f0b", "#fac775")
    TAG_GRAY   = ("#f1f4f9", "#475569", "#e2e8f0")

    FONT_MONO = ("Consolas", "Courier New", "monospace")
    FONT_UI   = ("Segoe UI", "Helvetica Neue", "Arial", "sans-serif")
