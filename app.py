from flask import Flask, render_template, request
from main import call_openai_function_call, match_id_with_name_web, store_records_in_db, validate_behavior_records
from toy_db import SessionLocal


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

        with SessionLocal() as session:
            prepared_notes = []
            for record in parsed_notes:
                match_result = match_id_with_name_web(record, session)

                # split fields as before
                simple, nested = split_notes(record)

                prepared_notes.append({
                    "simple": simple,
                    "nested": nested,
                    "candidate_students": match_result["candidate_students"],
                    "student_id": match_result["student_id"],
                    "student_name": match_result["student_name"],
                })

        return render_template(
            "review.html",
            original_note=teacher_note,
            parsed_notes=prepared_notes
        )
    
    @app.route("/review",methods=["POST"])
    def review():
        from werkzeug.datastructures import MultiDict
        from collections import defaultdict

        form_data = MultiDict(request.form)

        record_indices = set()
        for key in form_data.keys():
            if key.startswith("record_"):
                parts = key.split("_")
                if len(parts) >= 2:
                    record_indices.add(int(parts[1]))


        reconstructed_records = []

        for idx in sorted(record_indices):
                record = {}
                prefix = f"record_{idx}_"

                for key, value in form_data.items():
                    if key.startswith(prefix):
                        field_name = key[len(prefix):]
                        record[field_name] = value.strip() if isinstance(value, str) else value

                reconstructed_records.append(record)

        original_note = form_data.get("original_note", "")        

        # Validate records
        validated, failed = validate_behavior_records(reconstructed_records)

        with SessionLocal() as session:
            store_records_in_db(validated, session)
            session.commit()

        return render_template(
            "confirm.html",
            num_saved=len(validated),
            num_failed=len(failed),
            original_note=original_note
        )

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)