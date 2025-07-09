from flask import Flask, render_template, request, session
from services.open_ai_client import call_openai_function_call
from services.db import SessionLocal
from tools import tools
from schemas import BehaviorRecord
from services.matching import extract_records, match_id_exact, match_id_fuzzy, get_num_records


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
    num_records = get_num_records(form_data)
    records = extract_records(form_data,num_records)


    results = []
    with SessionLocal() as session:
        for record in records:
            result = match_id_exact(record, session)
            results.append(result)



    return render_template(
        "confirm.html",
        num_records=num_records,
        form_data=form_data,
        results=results
    )

print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    app.run(debug=True)
