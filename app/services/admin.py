from fastapi import HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.services.auth import register, require_roles
from app.schemas.Users import TeacherCreate, StudentCreate, TeacherAssignSubject, TeacherAssignClass, StudentAssignClass
from app.schemas.Class import ClassCreate
from app.schemas.Subject import SubjectCreate 
from app.models.models import Class, User, Subject, Teacher, TeacherClass, Student



# User Related Services
def create_teacher(newTeacherUser:TeacherCreate, db:Session, request:Request):
    require_roles(['admin'], request=request,db=db)
    return register(newuser=newTeacherUser, db=db, UserRole='teacher')

def create_student(newStudentUser: StudentCreate, db :Session, request:Request):
    # require_roles(['admin'], request=request,db=db)
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
    # require_roles(['admin'], request=request,db=db)

    teachers_list = []

    # Iterate over Teacher profiles. Each teacher may have zero or more TeacherClass assignments.
    # eager-load related objects to avoid N+1 queries
    teacher_profiles = db.query(Teacher).options(
        joinedload(Teacher.user),
        joinedload(Teacher.subject),
        joinedload(Teacher.teacher_classes).joinedload(TeacherClass.class_)
    ).all()
    for teacher in teacher_profiles:
        user = getattr(teacher, 'user', None)
        subject = getattr(teacher, 'subject', None)

        # If teacher has class assignments, return one entry per assignment
        if teacher.teacher_classes:
            for tc in teacher.teacher_classes:
                class_ = getattr(tc, 'class_', None)
                teachers_list.append({
                    'teacher_id': teacher.id,
                    'full_name': user.full_name if user else None,
                    'email': user.email if user else None,
                    'subject_name': subject.name if subject else None,
                    'class_standard': class_.standard if class_ else None,
                    'class_section': class_.section if class_ else None,
                    'is_class_teacher': tc.is_class_teacher
                })
        else:
            # No class assigned yet
            teachers_list.append({
                'teacher_id': teacher.id,
                'full_name': user.full_name if user else None,
                'email': user.email if user else None,
                'subject_name': subject.name if subject else None,
                'class_standard': None,
                'class_section': None,
                'is_class_teacher': False
            })

    return teachers_list


def all_student(db:Session, request :Request ):
    # require_roles(['admin'], request=request, db=db)

    student_list = []

    # Eager-load related objects to avoid N+1 queries
    student_profiles = db.query(Student).options(
        joinedload(Student.user),
        joinedload(Student.class_).joinedload(Class.teacher_classes).joinedload(TeacherClass.teacher).joinedload(Teacher.user),
    ).all()

    for student in student_profiles:
        user = getattr(student, 'user', None)
        class_ = getattr(student, 'class_', None)

        # Find class teacher (prefer TeacherClass with is_class_teacher=True)
        class_teacher_name = None
        if class_ and class_.teacher_classes:
            # prefer the TC marked as class teacher
            for tc in class_.teacher_classes:
                if tc.is_class_teacher:
                    teacher_profile = getattr(tc, 'teacher', None)
                    teacher_user = getattr(teacher_profile, 'user', None) if teacher_profile else None
                    class_teacher_name = teacher_user.full_name if teacher_user else None
                    break
            # fallback: if none marked, use first assigned teacher
            if class_teacher_name is None and class_.teacher_classes:
                tc = class_.teacher_classes[0]
                teacher_profile = getattr(tc, 'teacher', None)
                teacher_user = getattr(teacher_profile, 'user', None) if teacher_profile else None
                class_teacher_name = teacher_user.full_name if teacher_user else None

        student_list.append({
            'id': student.id,
            'user_id': student.user_id,
            'roll_number': student.roll_number,
            'standard': class_.standard if class_ else None,
            'section': class_.section if class_ else None,
            'class_teacher': class_teacher_name
        })

    return student_list


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
        User.id == teacher_data.teacher_id
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


## Student Class Relations

def assing_class_to_student(student_data:StudentAssignClass ,db:Session,request:Request):
    require_roles(['admin'],request=request, db=db)
    
    is_student_user = db.query(Student).filter(
        Student.user_id == student_data.student_id
    ).first()
    
    if is_student_user:
        raise HTTPException(status_code=404, detail=f"Student Already Assigned Class!!")
    
    # Ensure the referenced user exists
    is_user = db.query(User).filter(User.id == student_data.student_id).first()
    if not is_user:
        # Return an HTTP-friendly error instead of allowing a DB IntegrityError
        raise HTTPException(status_code=404, detail=f"Student User Not Found!!")

    # Ensure the class exists
    is_class = db.query(Class).filter(Class.id == student_data.class_id).first()
    if not is_class:
        raise HTTPException(status_code=404, detail=f"Class Not Found!!")
    
    new_student = Student(
        user_id = student_data.student_id,
        class_id = student_data.class_id,
        roll_number = student_data.roll_number
    )
    db.add(new_student)
    try:
        db.commit()
        db.refresh(new_student)
    except IntegrityError as e:
        db.rollback()
        # Convert DB integrity errors into HTTPExceptions with a helpful message
        raise HTTPException(status_code=400, detail=f"Could not assign student to class: {str(e.orig)}")

    return new_student


## Notice related Services
from app.models.models import Notice
from app.schemas.Notice import NoticeCreate, NoticeResponse

def create_notice(noticedata:NoticeCreate, db:Session, request:Request ):
    require_roles(['admin,teacher'],request=request,db=db)
    # Exactly one of class_id or standard must be provided (mutually exclusive)
    has_class = bool(noticedata.class_id)
    has_standard = bool(noticedata.standard)
    if has_class == has_standard:
        # either both provided or both missing
        raise HTTPException(status_code=400, detail="Provide exactly one of 'class_id' or 'standard'")

    # If class_id provided, ensure the class exists
    if noticedata.class_id:
        is_class = db.query(Class).filter(Class.id == noticedata.class_id).first()
        if not is_class:
            raise HTTPException(status_code=404, detail="Class not found for given class_id")

    new_notice = Notice(
        title = noticedata.title,
        description = noticedata.description,
        created_by = noticedata.created_by,
        class_id = noticedata.class_id or None,
        standard = noticedata.standard or None   
    )
    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)
    return new_notice

def delete_notice(notice_id: UUID, db:Session, request:Request):
    
    is_notice = db.query(Notice).filter(Notice.id == notice_id).first()
    
    if not is_notice:
        raise HTTPException(status_code=404, detail="Notice not found for given notice_id")
    
    db.delete(is_notice)
    db.commit()
    
    return f"{is_notice.title} is Deleted Successfully!!!"

def all_notices(db:Session, request:Request):
    require_roles(['admin', 'teacher'], request=request, db=db)
    notices = db.query(Notice).all()
    return notices        