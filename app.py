from flask import Flask, render_template, request
from main import call_openai_function_call

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def home():
        return render_template("index.html")

    @app.route("/submit", methods=["POST"])
    def submit():
        teacher_note = request.form["user_input"]
        parsed_notes = call_openai_function_call(teacher_note)
        # assume parsed_note is a dict already
        return render_template(
            "review.html",
            original_note=teacher_note,
            parsed_notes=parsed_notes
        )

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)