from db import SessionLocal, Student, BehaviorRecordDB, Course, student_course

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