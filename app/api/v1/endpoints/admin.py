from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.Users import UserResponse, UserResponseWithID,TeacherCreate, StudentCreate
from app.schemas.Class import ClassCreate, ClassResponse, ClassResponseWithID
from app.schemas.Subject import SubjectCreate, SubjectResponse, SubjectResponseWithID
from app.services.admin import create_teacher,  create_student, create_class, create_subject
from app.services.admin import all_classes, all_users, all_subjects
from app.services.admin import delete_class, delete_subject, delete_user


admin_router = APIRouter()


# User Related Services
@admin_router.post('/register_teacher',response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_teacher(newTeacherData:TeacherCreate, request:Request, db:Session=Depends(get_db)):
    return create_teacher(newTeacherUser=newTeacherData, db=db, request=request)

@admin_router.post('/register_student', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_student(newStudentData:StudentCreate, request:Request, db:Session=Depends(get_db)):
    return create_student(newStudentUser=newStudentData, db=db, request=request)

@admin_router.get('/all_users', response_model=list[UserResponseWithID], status_code=status.HTTP_200_OK)
def get_all_users(request:Request, db:Session=Depends(get_db)):
    return all_users(db=db, request=request)

@admin_router.delete('/delete_user/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_user(user_id: UUID, request:Request, db:Session=Depends(get_db)):
    return delete_user(user_id=user_id,db=db,request=request)

# Class Related Services
@admin_router.post('/create_class',response_model=ClassResponse,status_code=status.HTTP_201_CREATED)
def add_class(classData: ClassCreate, request:Request, db: Session=Depends(get_db)):
    return create_class(newClass=classData, db=db, request=request)

@admin_router.get('/all_classes', response_model=list[ClassResponseWithID], status_code=status.HTTP_200_OK)
def get_all_classes(request:Request, db:Session=Depends(get_db)):
    return all_classes(db=db, request=request)

@admin_router.delete('/delete_class/{class_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_class(class_id: UUID, request:Request, db:Session=Depends(get_db)):
    return delete_class(class_id=class_id, db=db, request=request)

# Subject Related Services
@admin_router.post('/create_subject',response_model=SubjectResponse,status_code=status.HTTP_201_CREATED)
def add_class(subjectdata: SubjectCreate, request:Request, db: Session=Depends(get_db)):
    return create_subject(newSubject =subjectdata, db=db, request=request)


@admin_router.get('/all_subjects', response_model=list[SubjectResponseWithID], status_code=status.HTTP_200_OK)
def get_all_subjects(request:Request, db:Session=Depends(get_db)):
    return all_subjects(db=db, request=request)

@admin_router.delete('/delete_subject/{subject_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_subject(subject_id: UUID, request:Request, db:Session=Depends(get_db)):
    return delete_subject(subject_id=subject_id, db=db, request=request)