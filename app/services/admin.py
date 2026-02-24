from fastapi import HTTPException, Request
from sqlalchemy.orm import Session 
from uuid import UUID
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

def delete_user(user_id: UUID, db:Session, request:Request):
    require_roles(['admin'],request=request, db=db)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"Class with id {user_id} not found!!")
    
    db.delete(user)
    db.commit()
    
    return {"detail": f"User {user.full_name} deleted successfully!! "}

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

def delete_subject(subject_id: UUID, db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject with id {subject_id} not found!!")
    
    db.delete(subject)
    db.commit()
    
    return {"detail": f"Subject with id {subject_id} deleted successfully!!"}


