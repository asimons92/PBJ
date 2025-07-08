from flask import Flask, render_template, request
from main import call_openai_function_call

def create_app():
    app = Flask(__name__)

    def split_notes(records):
        """
        Split a dict into flat/simple and nested fields.
        """
        simple_fields = {}
        nested_fields = {}

        for key, value in records.items():
            if isinstance(value, dict):
                nested_fields[key] = value
            else:
                simple_fields[key] = value
        return simple_fields, nested_fields

    @app.route("/", methods=["GET"])
    def home():
        return render_template("index.html")

    @app.route("/submit", methods=["POST"])
    def submit():
        teacher_note = request.form["user_input"]
        parsed_notes = call_openai_function_call(teacher_note)
        
        for record in parsed_notes:
            match_result = match_id_with_name_web(record, session)
            record["student_id"] = match_result["student_id"]
            record["candidate_students"] = match_result["candidate_students"]


        # Process each record to split fields
        prepared_notes = []
        for record in parsed_notes:
            simple, nested = split_notes(record)
            prepared_notes.append({
                "simple": simple,
                "nested": nested
            })

        return render_template(
            "review.html",
            original_note=teacher_note,
            parsed_notes=prepared_notes
        )
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)