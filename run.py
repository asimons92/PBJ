from flask import Flask, render_template, request, session
from services.open_ai_client import call_openai_function_call
from services.db import SessionLocal
from tools import tools
from schemas import BehaviorRecord
from services.matching import extract_records, match_id_exact, match_id_fuzzy


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
        original_note=teacher_note,
        parsed_notes=normalized_records
    )

@app.route("/review", methods=["POST"])
def review():
    form_data = request.form

    def get_num_records(form):
        indices = set()
        for key in form.keys():
            if key.startswith("record_"):
                parts = key.split("_")
                if len(parts) >= 3:
                    indices.add(int(parts[1]))
        return max(indices) + 1 if indices else 0
    
    num_records = get_num_records(form_data)
    records = extract_records(request.form,num_records)

    with SessionLocal() as session:
        for record in records:
            result = match_id_exact(record, session)
            print(f"Result from match_id: {result}")



    return render_template(
        "confirm.html",
        num_records=num_records,
        form_data=form_data,
        result=result
    )

print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    app.run(debug=True)
