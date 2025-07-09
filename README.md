# PB&J: Positive Behavior & JSON Teaching Assistant

**PB&J** is a prototype teacher's assistant tool that uses OpenAI’s function calling and Pydantic validation to parse unstructured teacher behavior notes into structured JSON data. It will integrate with the Canvas LMS to sync student and course information, validate parsed data, match students by name, and store behavior events for analysis and intervention.

Current Functionality:
- Basic Flask app takes typed teacher note, displays parsed noted, allows edits to parsed note. 
- Matching to student id in toy db, fuzzy matching within 80% threshold
    - Does not handle no-matches through UI yet (ie, nicknames)

Upcoming Functionality
- Navbar for note upload, Canvas functionality, view behavior record db
- Integrate Canvas syncing to Flask app (code exists in backend)
- Handle nicknames. 
- Anonymization of student data
- Host on Heroku for small scale testing with multiple users. 

Future Developments
- Run classification models on student behaviors for grouping, seating charts.
- Authenticate using Canvas LMS login (instead of generating API key)
- Pretty UI



This is a personal prototype. The code is provided here for demonstration and feedback. Please don’t reuse or redistribute it without asking — thanks!

