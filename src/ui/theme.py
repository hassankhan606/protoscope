"""
BioDiscover Color Theme
Dark biotech-inspired palette with phosphorescent green accents.
"""


class BioTheme:
    # Backgrounds (darkest → lightest)
    BG_DARK   = "#0d1117"   # Page background
    BG_PANEL  = "#161b22"   # Sidebar / header
    BG_MID    = "#1c2330"   # Cards, active nav
    BG_CARD   = "#21293a"   # Data cards

    # Accents
    ACCENT_GREEN  = "#39d353"   # Primary — DNA-sequencer green
    ACCENT_BLUE   = "#58a6ff"   # Secondary — electron-blue
    ACCENT_PURPLE = "#bc8cff"   # Tertiary — molecular purple
    ACCENT_ORANGE = "#f0883e"   # Warning / enzymes
    ACCENT_RED    = "#ff7b72"   # Error / stop codon

    # Text
    TEXT_MAIN = "#e6edf3"   # Primary text
    TEXT_DIM  = "#8b949e"   # Labels, subtitles
    TEXT_FAINT= "#484f58"   # Placeholder

    # Borders
    BORDER    = "#30363d"

    # Tag colours for functional annotations
    TAG_COLORS = {
        "enzyme":     ("#f0883e", "#0d1117"),
        "receptor":   ("#58a6ff", "#0d1117"),
        "kinase":     ("#bc8cff", "#0d1117"),
        "transporter":("#39d353", "#0d1117"),
        "channel":    ("#ff7b72", "#0d1117"),
        "default":    ("#8b949e", "#0d1117"),
    }

    # Font families (fall-back chain)
    FONT_MONO   = ("Consolas", "Courier New", "monospace")
    FONT_UI     = ("Segoe UI", "Helvetica Neue", "sans-serif")

    def tag_color(self, keyword: str):
        kw = keyword.lower()
        for key in self.TAG_COLORS:
            if key in kw:
                return self.TAG_COLORS[key]
        return self.TAG_COLORS["default"]
