from canvasapi import Canvas
from dotenv import load_dotenv
from services.db import SessionLocal, Student, Course
import os


load_dotenv()

API_BASE_URL = "https://reviewer.instructure.com"  #This should be user inputted eventually
ACCESS_TOKEN = os.getenv('CANVAS_API_KEY')

canvas = Canvas(API_BASE_URL,ACCESS_TOKEN)

def get_canvas_courses():
    me = canvas.get_current_user()
    courses = list(me.get_courses())
    if courses:
        course_dict = {}
        for course in courses:
            #Save all course names and ids
            course_dict[course.id] = course.name
        for course_id, name in course_dict.items():
            print(f"Course name is: {name} and its ID is {course_id}")

            
    else:
        print("Courses not found.")
    return course_dict



def get_canvas_students(courses):
    student_course_map = {}

    for course_id in courses.keys():
        course_obj = canvas.get_course(course_id)
        
        # ⚡ Request enrollments in same API call
        users = list(course_obj.get_users(enrollment_type=['student'], include=['enrollments']))

        students = []
        for user in users:
            enrollments = getattr(user, 'enrollments', [])
            section_id = None
            for enrollment in enrollments:
                if enrollment.get("type") == "StudentEnrollment":
                    section_id = str(enrollment.get("course_section_id"))
                    break

            students.append({
                "canvas_id": str(user.id),
                "name": user.name,
                "email": getattr(user, 'email', None),
                "section_id": section_id
            })

        student_course_map[course_id] = students

    return student_course_map


def sync_canvas_students(course_dict):
    with SessionLocal() as session:
        student_course_map = get_canvas_students(course_dict)

        for course_id, students in student_course_map.items():
            course = session.query(Course).filter_by(canvas_course_id=course_id).first()
            if not course:
                print(f"Course ID {course_id} not found in DB. Skipping.")
                continue

            for s in students:
                student = session.query(Student).filter_by(canvas_user_id=int(s["canvas_id"])).first()

                if not student:
                    student = Student(
                        canvas_user_id=int(s["canvas_id"]),
                        name=s["name"],
                        email=s["email"]
                    )
                    session.add(student)

                if course not in student.courses:
                    student.courses.append(course)

        session.commit()

def sync_canvas_courses():
    courses = get_canvas_courses()
    with SessionLocal() as session:
        for course_id, course_name in courses.items():
            existing = session.query(Course).filter_by(canvas_course_id=course_id).first()
            if not existing:
                session.add(Course(name=course_name, canvas_course_id=course_id))
        session.commit()
    return courses  

# Main sync logic
course_dict = sync_canvas_courses()  # now includes course_dict
sync_canvas_students(course_dict)


