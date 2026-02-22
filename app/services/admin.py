from fastapi import HTTPException, Request
from sqlalchemy.orm import Session 
from sqlalchemy import func

from app.services.auth import register, require_roles
from app.schemas.Users import TeacherCreate, StudentCreate
from app.schemas.Class import ClassCreate
from app.schemas.Subject import SubjectCreate 
from app.models.models import Class, User, Subject



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


## sybject related services

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
