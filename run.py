from flask import Flask, render_template, request
from services.open_ai_client import call_openai_function_call
from services.db import SessionLocal

app = Flask(__name__)
app.secret_key = "supersecret"  # update to pull from env

@app.route("/", methods=["GET"])
def home():
    print("home() route called")
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    teacher_note = request.form["user_input"]
    parsed_notes = call_openai_function_call(teacher_note)
    return render_template(
        "review.html",
        original_note=teacher_note,
        parsed_notes=parsed_notes
    )

@app.route("/review", methods=["POST"])
def review():
    form_data = request.form
    return render_template(
        "confirm.html",
        form_data=form_data
    )

print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    app.run(debug=True)
