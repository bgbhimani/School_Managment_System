import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"

class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    teacher = relationship("Teacher", back_populates="user", uselist=False)
    student = relationship("Student", back_populates="user", uselist=False)
    
class Class(Base):
    __tablename__ = "classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    standard = Column(Integer, nullable=False)
    section = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    students = relationship("Student", back_populates="class_")
    teacher_classes = relationship("TeacherClass", back_populates="class_")
    tests = relationship("Test", back_populates="class_")
    attendance_sessions = relationship("AttendanceSession", back_populates="class_")
    
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)

    teachers = relationship("Teacher", back_populates="subject")
    tests = relationship("Test", back_populates="subject")
    
class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)

    user = relationship("User", back_populates="teacher")
    subject = relationship("Subject", back_populates="teachers")
    teacher_classes = relationship("TeacherClass", back_populates="teacher")
    tests = relationship("Test", back_populates="teacher")
    attendance_sessions = relationship("AttendanceSession", back_populates="teacher")

class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    roll_number = Column(Integer, nullable=False)

    user = relationship("User", back_populates="student")
    class_ = relationship("Class", back_populates="students")
    attendance_records = relationship("AttendanceRecord", back_populates="student")
    test_results = relationship("TestResult", back_populates="student")
    
class TeacherClass(Base):
    __tablename__ = "teacher_classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    is_class_teacher = Column(Boolean, default=False)

    teacher = relationship("Teacher", back_populates="teacher_classes")
    class_ = relationship("Class", back_populates="teacher_classes")
    
class Notice(Base):
    __tablename__ = "notices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True)
    standard = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User")
    
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    date = Column(Date, nullable=False)

    class_ = relationship("Class", back_populates="attendance_sessions")
    teacher = relationship("Teacher", back_populates="attendance_sessions")
    records = relationship("AttendanceRecord", back_populates="session")
     
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)

    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("Student", back_populates="attendance_records")
    
class Test(Base):
    __tablename__ = "tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    title = Column(String, nullable=False)
    total_marks = Column(Integer, nullable=False)
    test_date = Column(Date, nullable=False)

    class_ = relationship("Class", back_populates="tests")
    subject = relationship("Subject", back_populates="tests")
    teacher = relationship("Teacher", back_populates="tests")
    results = relationship("TestResult", back_populates="test")  
    
class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    marks_obtained = Column(Integer, nullable=False)

    test = relationship("Test", back_populates="results")
    student = relationship("Student", back_populates="test_results")

