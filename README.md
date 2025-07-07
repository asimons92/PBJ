# PB&J: Positive Behavior & JSON Teaching Assistant

**PB&J** is a prototype teacher's assistant tool that uses OpenAI’s function calling and Pydantic validation to parse unstructured teacher behavior notes into structured JSON data. It integrates with the Canvas LMS to sync student and course information, validates parsed data, matches students by name, and stores behavior events for analysis and intervention.

---
## Features

- Uses OpenAI API function calling to extract structured behavior records from free-text teacher notes.
- Validates parsed data with Pydantic schemas to ensure data consistency.
- Syncs with Canvas LMS to keep student and course data up to date.
    - You would need a Canvas API key to test this functionality. Just use included database instead if you don't use Canvas.
- Fuzzy matching to assign student IDs from parsed names.
- Checks for nicknames, missing course assignment. 
- Stores behavior data in a SQLite database with SQLAlchemy ORM.
- Preparing for future enhancements like voice input, anonymization, and ML classifiers for seating and group arrangments. 
---

## Repo Structure
PBJ/
├── README.md # Project overview and instructions
├── requirements.txt # Python dependencies
├── toy_db.py # Database setup and SQLAlchemy models
├── canvas.py # Canvas API integration and sync logic
├── schemas.py # Pydantic schemas for validation
├── main.py # OpenAI API function calling logic
├── notes/ # Example teacher notes input files
│ └── example_note.txt
│ └── example_note2.txt
│ └── example_note3.txt
├── outputs/ # Sample parsed JSON output
│ └── parsed_behavior.json
└── tools.py # Tool call 
└── toy_canvas.db # toy database (set up by running toy_db.py)

This is a personal prototype. The code is provided here for demonstration and feedback. Please don’t reuse or redistribute it without asking — thanks!

