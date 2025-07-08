from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Table, DateTime, JSON, Boolean  # Added DateTime and JSON imports
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os

Base = declarative_base()

# Many to many association table
student_course = Table(
    'student_course',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)


# Make student model
class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    canvas_user_id = Column(Integer, unique=True)
    name = Column(String)
    email = Column(String)

    courses = relationship("Course", secondary=student_course, back_populates="students")
    behavior_records = relationship("BehaviorRecordDB", back_populates="student")  # Added relationship to new model



# Make course model
class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    canvas_course_id = Column(Integer, unique=True)
    name = Column(String)

    students = relationship("Student", secondary=student_course, back_populates="courses")

class BehaviorRecordDB(Base):
    __tablename__ = 'behavior_records'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=True)  # Add course reference
    source = Column(String, nullable=False)
    recording_timestamp = Column(DateTime, nullable=False)
    behavior_date = Column(DateTime, nullable=True)

        # Behavior fields
    behavior_category = Column(String)
    behavior_description = Column(Text)
    behavior_severity = Column(String)
    behavior_is_positive = Column(Boolean)
    behavior_needs_followup = Column(Boolean)
    behavior_tags = Column(Text)  # JSON string

        # Context fields
    context_class_name = Column(String)
    context_teacher = Column(String)
    context_activity = Column(String)
    context_location = Column(String)

        # Intervention fields
    intervention_status = Column(String)
    intervention_type = Column(String)
    intervention_notes = Column(Text)
    intervention_tier = Column(String)


    student = relationship("Student", back_populates="behavior_records")
    course = relationship("Course")  # Add course relationship

#set up db
engine = create_engine("sqlite:///toy_canvas.db", echo=True)
SessionLocal = sessionmaker(bind=engine)

# add dummy data
def add_dummy_data():
    session = SessionLocal()

    # Create 4th period History course
    history_course = Course(canvas_course_id=404, name="4th Period History")
    science_course = Course(canvas_course_id=505, name="5th Period Science")

    # Create students based on teacher notes
    students = [
        Student(canvas_user_id=1001, name="Molly", email="molly@example.com", courses=[history_course]),
        Student(canvas_user_id=1002, name="Sarah", email="sarah@example.com", courses=[history_course]),
        Student(canvas_user_id=1003, name="Anna", email="anna@example.com", courses=[history_course,science_course]),
        Student(canvas_user_id=1004, name="Collin", email="collin@example.com", courses=[history_course]),
        Student(canvas_user_id=1005, name="Brad", email="brad@example.com", courses=[history_course]),
        Student(canvas_user_id=1006, name="Emily", email="emily@example.com", courses=[history_course]),
        Student(canvas_user_id=1007, name="Alex", email="alex@example.com", courses=[history_course]),
        Student(canvas_user_id=1008, name="John", email="john@example.com", courses=[history_course]),
        Student(canvas_user_id=1009, name="Kyle", email="kyle@example.com", courses=[history_course]),
        Student(canvas_user_id=1010, name="Mike", email="mike@example.com", courses=[history_course]),
        Student(canvas_user_id=1011, name="Emma", email="emma@example.com", courses=[history_course]),
    ]

    session.add(history_course)
    session.add_all(students)
    session.commit()
    session.close()

def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    add_dummy_data()