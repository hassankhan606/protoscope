#!/bin/bash
echo "================================================"
echo "  BioDiscover - Quick Setup (macOS / Linux)"
echo "================================================"
echo ""

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
echo "Done."

echo ""
echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo ""
echo "[3/4] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "[4/4] All done! Run the app with:"
echo "  python src/main.py"
echo ""
