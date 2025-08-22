#!/usr/bin/env python3
"""
Migration script to populate the approved_teachers collection with existing teachers.
Run this script once to initialize the database with the current teachers.
"""

import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from extensions import mongo
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mongo.init_app(app)
    return app

def migrate_teachers():
    """Add existing teachers to the approved_teachers collection"""
    app = create_app()
    
    with app.app_context():
        # List of existing teachers from the hardcoded template
        existing_teachers = [
            "Baskaran V",
            "Sugapriya S", 
            "Balaji A",
            "Latha J",
            "Dhanalakshmi R",
            "Vinothkumar M",
            "Anand V",
            "Archana G.M",
            "Kirubakaran Amalraj"
        ]
        
        print("Starting teacher migration...")
        
        # Check if collection already has data
        existing_count = mongo.db.approved_teachers.count_documents({})
        if existing_count > 0:
            print(f"Found {existing_count} existing teachers in database.")
            response = input("Do you want to add the hardcoded teachers anyway? (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled.")
                return
        
        # Add teachers to the database
        added_count = 0
        for teacher_name in existing_teachers:
            # Check if teacher already exists
            if not mongo.db.approved_teachers.find_one({"name": teacher_name}):
                mongo.db.approved_teachers.insert_one({
                    "name": teacher_name,
                    "created_at": datetime.now()
                })
                print(f"Added: {teacher_name}")
                added_count += 1
            else:
                print(f"Already exists: {teacher_name}")
        
        print(f"\nMigration completed! Added {added_count} new teachers.")
        total_count = mongo.db.approved_teachers.count_documents({})
        print(f"Total teachers in database: {total_count}")

if __name__ == "__main__":
    migrate_teachers()
