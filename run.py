from flask import Flask, render_template, request, session
from services.open_ai_client import call_openai_function_call
from services.db import SessionLocal
from tools import tools
from schemas import BehaviorRecord


app = Flask(__name__)
app.secret_key = "supersecret"  # update to pull from env

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    teacher_note = request.form["user_input"] 
    raw_json = call_openai_function_call(teacher_note)

    normalized_records = [
        BehaviorRecord(**raw_record).dict()
        for raw_record in raw_json
    ]

    session["note_json"] = normalized_records

    return render_template(
        "review.html",
        original_note=raw_json,
        parsed_notes=normalized_records
    )

@app.route("/review", methods=["POST"])
def review():
    note = session.get("note_json")
    return render_template(
        "confirm.html",
        form_data=note
    )

print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    app.run(debug=True)
