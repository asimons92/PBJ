from db import SessionLocal, Student, BehaviorRecordDB, Course, student_course


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
        match_id_fuzzy(record)
        ###

def match_id_fuzzy(record,session,similarity_thresh=80):
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

with SessionLocal() as session:
    courses = pull_courses_from_db(session)
    for course in courses:
        print(course.name)
        print(course.id)
    print("What course?")
    user_selection = input()
    selected_course = None
    for course in courses:
        if str(course.id) == user_selection or course.name == user_selection:
            selected_course = course
            break

    if selected_course:
        print(f"Selected course: {selected_course.name} (ID: {selected_course.id})")
    else:
        print("Course not found.")
    
    students = pull_students_from_course(selected_course)
    for s in students:
        print(s.name)