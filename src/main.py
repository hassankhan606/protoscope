"""
BioDiscover - Biotech Discovery Platform
A comprehensive tool for PhD students and researchers to explore
proteins, genes, pathways, and molecular structures.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.main_window import BioDiscoverApp


def main():
    root = tk.Tk()
    root.title("BioDiscover — Biotech Discovery Platform")
    root.geometry("1400x900")
    root.minsize(1100, 700)

    # Set app icon if available
    try:
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            img = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, img)
    except Exception:
        pass

    app = BioDiscoverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
