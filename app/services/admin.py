from fastapi import HTTPException, Request
from sqlalchemy.orm import Session 
from uuid import UUID
from sqlalchemy import func

from app.services.auth import register, require_roles
from app.schemas.Users import TeacherCreate, StudentCreate, TeacherAssignSubject, TeacherAssignClass
from app.schemas.Class import ClassCreate
from app.schemas.Subject import SubjectCreate 
from app.models.models import Class, User, Subject, Teacher, TeacherClass



# User Related Services
def create_teacher(newTeacherUser:TeacherCreate, db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    return register(newuser=newTeacherUser, db=db, UserRole='teacher')

def create_student(newStudentUser: StudentCreate, db :Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    return register(newuser=newStudentUser, db=db, UserRole='student')

def all_users(db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    users = db.query(User).all()
    return users

def delete_user(user_id: UUID, db:Session, request:Request):
    require_roles(['admin'],request=request, db=db)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"Class with id {user_id} not found!!")
    
    db.delete(user)
    db.commit()
    
    return {"detail": f"User {user.full_name} deleted successfully!! "}

def all_teachers(db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    teachers = db.query(Teacher).all()
    return teachers


## class Related Services

def create_class(newClass:ClassCreate, db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    
    is_class = db.query(Class).filter(
        Class.standard == newClass.standard,
        Class.section == newClass.section
    ).first()
    
    if is_class:
        raise HTTPException(status_code=401, detail=f"Class {newClass.standard} {newClass.section} Already Exists!!")
    
    new_Class = Class(
        section = newClass.section,
        standard = newClass.standard 
    )
    
    db.add(new_Class)
    db.commit()
    db.refresh(new_Class)
    
    return new_Class

def all_classes( db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    classes = db.query(Class).all()
    return classes

def delete_class(class_id: UUID, db:Session, request:Request):
    require_roles(['admin'], request=request, db=db)
    
    classtoremove = db.query(Class).filter(Class.id == class_id).first()
    
    if not classtoremove:
        raise HTTPException(status_code=404, detail=f"Class with id {class_id} not found!!")
    
    db.delete(classtoremove)
    db.commit()
    
    return {"detail": f"Class with id {class_id} deleted successfully!! "}



## subject related services

def all_subjects(db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    subjects = db.query(Subject).all()
    return subjects

def create_subject(newSubject: SubjectCreate, db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    
    is_subject = db.query(Subject).filter(
        func.lower(Subject.name) == func.lower(newSubject.name)
    ).first()
    
    if is_subject:
        raise HTTPException(status_code=401, detail=f"Class {newSubject.name} Already Exists!!")
    
    new_subject = Subject(
        name = newSubject.name
    )
    
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    
    return new_subject

def delete_subject(subject_id: UUID, db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject with id {subject_id} not found!!")
    
    db.delete(subject)
    db.commit()
    
    return {"detail": f"Subject with id {subject_id} deleted successfully!!"}



## Teacher - Class - Subject Relations

def assign_sub_to_teacher( teacher_data: TeacherAssignSubject,db:Session, request:Request):
    
    require_roles(['admin'],request=request, db=db)
    
    # Check if this user already has a Teacher profile assigned to the same subject
    is_sub_assigned = db.query(Teacher).filter(
        Teacher.user_id == teacher_data.teacher_id,
        Teacher.subject_id == teacher_data.subject_id
    ).first()

    if is_sub_assigned:
        raise HTTPException(status_code=208, detail=f"Subject already assigned to the teacher")
        
    is_teacher = db.query(User).filter(
        User.id == teacher_data.teacher_id,
        User.role == 'teacher'
    ).first()
    
    if not is_teacher:
        raise HTTPException(status_code=404, detail=f"Teacher not Found!!")
    
    is_subject = db.query(Subject).filter(
        Subject.id == teacher_data.subject_id
    ).first()
    
    if not is_subject:
        raise HTTPException(status_code=404, detail=f"Subject not Found!!")
    
    new_teacher = Teacher(
        user_id = teacher_data.teacher_id,
        subject_id = teacher_data.subject_id
    )
    
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    
    return new_teacher
    
def assign_class_to_teacher(teacher_data:TeacherAssignClass ,db:Session, request: Request):
    require_roles(['admin'],request=request, db=db)
    
    # Ensure the User exists and has role 'teacher'
    is_teacher_user = db.query(User).filter(
        User.id == teacher_data.teacher_id,
        User.role == 'teacher'
    ).first()

    if not is_teacher_user:
        raise HTTPException(status_code=404, detail=f"Teacher user not found!!")

    # Lookup the Teacher profile (teachers table) for that user
    teacher_profile = db.query(Teacher).filter(Teacher.user_id == teacher_data.teacher_id).first()
    if not teacher_profile:
        raise HTTPException(status_code=404, detail="Teacher profile not found. Create a Teacher record first.")

    # Check class existence
    is_class = db.query(Class).filter(Class.id == teacher_data.class_id).first()
    if not is_class:
        raise HTTPException(status_code=404, detail=f"Class not Found!!")

    # Check if this teacher-class assignment already exists (use teacher_profile.id)
    is_class_assigned = db.query(TeacherClass).filter(
        TeacherClass.teacher_id == teacher_profile.id,
        TeacherClass.class_id == teacher_data.class_id
    ).first()

    if is_class_assigned:
        raise HTTPException(status_code=208, detail=f"Class already assigned to the teacher")

    new_teacher_class = TeacherClass(
        teacher_id = teacher_profile.id,
        class_id = teacher_data.class_id,
        is_class_teacher = teacher_data.is_class_teacher
    )
    
    db.add(new_teacher_class)
    db.commit()
    db.refresh(new_teacher_class)
    
    return new_teacher_class

def teacher_of_class(class_id: UUID, db: Session, request: Request):
    # require_roles(['admin', 'teacher'], request=request, db=db)
    is_class = db.query(Class).filter(Class.id == class_id).first()
    if not is_class:
        raise HTTPException(status_code=404, detail=f"Class not Found!!")
    
    teacher_class = db.query(TeacherClass).filter(TeacherClass.class_id == class_id).first()
    if not teacher_class:
        raise HTTPException(status_code=404, detail=f"No teacher assigned to this class!!")
    
    return teacher_class
