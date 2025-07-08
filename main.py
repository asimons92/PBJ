from openai import OpenAI
from datetime import datetime, UTC
import os
from dotenv import load_dotenv
import json
from schemas import BehaviorRecord
from pydantic import ValidationError
from toy_db import SessionLocal, Student, BehaviorRecordDB, Course, student_course
from fuzzywuzzy import fuzz, process


# --- Match ID and Name --- #
def match_id_with_name(record, session, similarity_threshold=80):
    student = session.query(Student).filter_by(name=record.student_name).first()
    if student:
        record.student_id = student.id
        record.student_name = student.name
        return True

    all_students = session.query(Student).all()
    student_names = [(s.name, s.id) for s in all_students]

    best_match = process.extractOne(
        record.student_name,
        [name for name, _ in student_names],
        scorer=fuzz.ratio
    )

    if best_match and best_match[1] >= similarity_threshold:
        matched_name = best_match[0]
        matched_student_id = next(sid for name, sid in student_names if name == matched_name)

        print(f"\nStudent name '{record.student_name}' not found exactly.")
        print(f"Did you mean '{matched_name}'? (similarity: {best_match[1]}%)")

        while True:
            choice = input("Enter 'y' for yes, 'n' for no, or 's' to skip this record: ").lower().strip()
            if choice == 'y':
                record.student_id = matched_student_id
                record.student_name = matched_name
                return True
            elif choice == 'n':
                return handle_manual_student_selection(record, session, student_names)
            elif choice == 's':
                return False
            else:
                print("Please enter 'y', 'n', or 's'")
    else:
        return handle_manual_student_selection(record, session, student_names)



def match_id_with_name_web(record, session, similarity_threshold=80):
    """
    Try to match a record's student name to a student in DB.
    If exact match: set student_id
    If fuzzy match: return candidate_students for UI
    """
    result = {
        "student_name": record.get("student_name"),
        "student_id": None,
        "candidate_students": []
    }

    # Try exact match
    student = session.query(Student).filter_by(name=record["student_name"]).first()
    if student:
        result["student_id"] = student.id
        result["student_name"] = student.name
        return result

    # No exact match → fuzzy match
    all_students = session.query(Student).all()
    student_names = [(s.name, s.id) for s in all_students]

    best_matches = process.extract(
        record["student_name"],
        [name for name, _ in student_names],
        scorer=fuzz.ratio,
        limit=5
    )

    for name, score in best_matches:
        if score >= similarity_threshold:
            student_id = next(sid for n, sid in student_names if n == name)
            result["candidate_students"].append({
                "name": name,
                "id": student_id,
                "similarity": score
            })

    print("Candidates for", record["student_name"], ":", result["candidate_students"]) #Debug print
    return result


def handle_manual_student_selection(record, session, student_names):
    print(f"\nStudent not found. Please select from available students:")
    for i, (name, student_id) in enumerate(student_names, 1):
        print(f"{i}. {name} (ID: {student_id})")

    while True:
        choice = input(f"Enter number (1-{len(student_names)}) to select a student, or 's' to skip: ").strip()
        if choice.lower() == 's':
            return False
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(student_names):
                selected_name, selected_id = student_names[idx]
                record.student_id = selected_id
                record.student_name = selected_name
                return True
            else:
                print(f"Please enter a number between 1 and {len(student_names)}")
        except ValueError:
            print("Please enter a valid number or 's' to skip")

def get_course_for_record(record, session):
    if record.context and record.context.class_name:
        course = session.query(Course).filter_by(name=record.context.class_name).first()
        if course:
            return course.id

    if not record.student_id:
        print("Student ID missing. Cannot determine enrolled courses.")
        return None

    enrolled_courses = (
        session.query(Course)
        .join(student_course)
        .filter(student_course.c.student_id == record.student_id)
        .all()
    )

    if not enrolled_courses:
        print(f"No enrolled courses found for student ID {record.student_id}.")
        return None

    print(f"\nSelect a course for student '{record.student_name}':")
    for i, course in enumerate(enrolled_courses, 1):
        print(f"{i}. {course.name} (ID: {course.canvas_course_id})")

    while True:
        choice = input(f"Enter number (1-{len(enrolled_courses)}) to select a course, or 's' to skip: ").strip()
        if choice.lower() == 's':
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(enrolled_courses):
                return enrolled_courses[idx].id
            else:
                print(f"Please enter a number between 1 and {len(enrolled_courses)}")
        except ValueError:
            print("Please enter a valid number or 's' to skip")

# --- Validation --- #
def validate_behavior_records(raw_records):
    validated = []
    failed = []
    for raw in raw_records:
        # Always set source to teacher_note to prevent validation failures
        raw['source'] = 'teacher_note'
        
        # Remove student_id if present since we'll set it after validation
        if 'student_id' in raw:
            del raw['student_id']
        
        try:
            record = BehaviorRecord(**raw)
            validated.append(record)
        except ValidationError as e:
            print("Validation failed for record:")
            print(e.json(indent=2))
            failed.append(raw)
    return validated, failed


def store_records_in_db(records, session):
    for record in records:
        # Use the enhanced match_id_with_name function
        if not match_id_with_name(record, session):
            continue

        course_id = get_course_for_record(record, session)
        if course_id is None:
            print(f"Skipping record for {record.student_name} - no course selected")
            continue

        # The record.student_id now contains the database id from match_id_with_name
        db_record = BehaviorRecordDB(
            student_id=record.student_id,  # This is now the database id
            course_id=course_id,  # Add course_id field
            source=record.source,
            recording_timestamp=record.recording_timestamp,
            behavior_date=record.behavior_date,
            # Behavior fields
            behavior_category=record.behavior.category if record.behavior else None,
            behavior_description=record.behavior.description if record.behavior else None,
            behavior_severity=record.behavior.severity if record.behavior else None,
            behavior_is_positive=record.behavior.is_positive if record.behavior else None,
            behavior_needs_followup=record.behavior.needs_followup if record.behavior else None,
            behavior_tags=json.dumps(record.behavior.tags) if record.behavior and record.behavior.tags else None,
            # Context fields
            context_class_name=record.context.class_name if record.context else None,
            context_teacher=record.context.teacher if record.context else None,
            context_activity=record.context.activity if record.context else None,
            context_location=record.context.location if record.context else None,
            # Intervention fields
            intervention_status=record.intervention.status if record.intervention else None,
            intervention_type=record.intervention.type if record.intervention else None,
            intervention_notes=record.intervention.notes if record.intervention else None,
            intervention_tier=record.intervention.tier if record.intervention else None
        )
        session.add(db_record)


# --- Main Workflow --- #
def main():
    input_path = os.path.join("notes", "example_note3.txt")
    output_path = os.path.join("outputs", "parsed_behavior.json")

    with open(input_path, "r") as f:
        note = f.read()

    parsed = call_openai_function_call(note)
    validated, failed = validate_behavior_records(parsed)

    with SessionLocal() as session:
        store_records_in_db(validated, session)

        if failed:
            print(f"Retrying {len(failed)} failed records...")
            retried = call_openai_function_call(note, retry=True)
            revalidated, _ = validate_behavior_records(retried)
            store_records_in_db(revalidated, session)

        session.commit()

    json_ready = [record.model_dump(mode='json') for record in validated]
    with open(output_path, "w") as f:
        json.dump(json_ready, f, indent=2)

    print(f"Saved to {output_path} and stored in the database.")


if __name__ == "__main__":
    main()