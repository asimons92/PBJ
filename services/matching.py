from services.db import SessionLocal, Student, BehaviorRecordDB, Course, student_course
from fuzzywuzzy import fuzz, process

def extract_records(form,num_records):
    records = []
    for i in range(num_records):
        record = {}
        for key,value in form.items():
            if key.startswith(f"record_{i}_"):
                field_name = key[len(f"record_{i}_"):]
                record[field_name] = value
            records.append(record) 
    return records

def match_id_exact(record, session):
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
    else:
        candidate_students = match_id_fuzzy(record,session)
        result["candidate_students"] = candidate_students
        return result

def match_id_fuzzy(record,session,similarity_threshold=80):
    candidate_students = []
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
            candidate_students.append({
                "name": name,
                "id": student_id,
                "similarity": score
            })

    return candidate_students
    


def pull_courses_from_db(session):
    courses = session.query(Course).all()
    return courses

def pull_students_from_course(course):
    students = course.students
    return students

