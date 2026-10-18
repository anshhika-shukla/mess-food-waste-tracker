"""
Root entry point for Smart Mess Food Feedback & Waste Analytics Tracker.
Allows running with:
    python main.py
or:
    uvicorn main:app --reload
"""
import sys
import os
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app

if __name__ == "__main__":
    print("Starting Smart Mess Food Feedback & Waste Analytics Tracker on http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
