"""
Root launcher for seeding realistic historical data into Smart Mess Food Feedback & Waste Tracker.
"""
import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.seed_data import seed_database

if __name__ == "__main__":
    seed_database()
