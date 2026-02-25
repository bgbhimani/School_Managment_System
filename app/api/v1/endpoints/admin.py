from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db

from app.schemas.Users import UserResponse, UserResponseWithID,TeacherCreate, StudentCreate, TeacherAssignSubject, TeacherAssignSubjectResponse, TeacherAssignClass, TeacherAssignClassResponse, TeacherListItem, StudentAssignClassResponse, StudentAssignClass, StudentListItem
from app.schemas.Notice import NoticeCreate, NoticeResponse, NoticeResponseWithID
from app.schemas.Class import ClassCreate, ClassResponse, ClassResponseWithID
from app.schemas.Subject import SubjectCreate, SubjectResponse, SubjectResponseWithID
from app.services.admin import create_teacher,  create_student, create_class, create_subject
from app.services.admin import all_classes, all_users, all_subjects, assign_sub_to_teacher, assign_class_to_teacher, all_teachers , all_student
from app.services.admin import delete_class, delete_subject, delete_user, teacher_of_class, assing_class_to_student
from app.services.admin import create_notice, delete_notice, all_notices


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

@admin_router.get('/all_teachers', response_model=list[TeacherListItem], status_code=status.HTTP_200_OK)
def get_all_teachers(request:Request, db:Session=Depends(get_db)):
    return all_teachers(db=db, request=request)

@admin_router.get('/all_students', response_model=list[StudentListItem])
def get_all_students(request: Request, db: Session = Depends(get_db)):
    return all_student(db=db, request=request)


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




# Teacher-Class-Subject Relations

@admin_router.post('/assign_subject',response_model=TeacherAssignSubjectResponse,status_code=status.HTTP_201_CREATED)
def assign_subject(teacher_data: TeacherAssignSubject,request: Request,  db: Session=Depends(get_db)):
    return assign_sub_to_teacher(teacher_data=teacher_data,db=db,request=request)

@admin_router.post('/assign_class', response_model=TeacherAssignClassResponse, status_code=status.HTTP_201_CREATED)
def assign_class(teacher_data: TeacherAssignClass, request: Request, db: Session=Depends(get_db)):
    return assign_class_to_teacher(teacher_data=teacher_data, db=db, request=request)

@admin_router.get('/teacher_of_class/{class_id}', response_model=TeacherAssignClassResponse, status_code=status.HTTP_200_OK)
def teacher_of_the_class(class_id: UUID, request: Request, db: Session=Depends(get_db)):
    return teacher_of_class(class_id=class_id, db=db, request=request)

## Student- Class Relation

@admin_router.post('/assign_class_to_student', response_model=StudentAssignClassResponse,status_code=status.HTTP_201_CREATED)
def assign_class_student(student_data:StudentAssignClass, request: Request, db:Session=Depends(get_db)):
    return assing_class_to_student(student_data=student_data, request=request, db=db)

@admin_router.post('/notice',response_model=NoticeResponse,status_code=status.HTTP_201_CREATED)
def add_notice(noticedata:NoticeCreate,request:Request ,db:Session=Depends(get_db)):
    return create_notice(noticedata=noticedata, request=request, db=db)

@admin_router.delete('/notice/{notice_id}',status_code=status.HTTP_202_ACCEPTED)
def remove_notice(notice_id:UUID, request:Request, db:Session=Depends(get_db)):
    return delete_notice(notice_id=notice_id, db=db,request=request)

@admin_router.get('/notice', response_model=list[NoticeResponseWithID], status_code=status.HTTP_200_OK)
def get_all_notices(request:Request, db:Session=Depends(get_db)):
    return all_notices(db=db, request=request)