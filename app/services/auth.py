from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session 
from sqlalchemy import func
from pwdlib import PasswordHash
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
import os
from app.schemas.Users import UserCreate, UserLogin
from app.models.models import User
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

password_hash = PasswordHash.recommended()


def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password,hashed_password)

def register(newuser: UserCreate,db:Session, UserRole: str = "student"):
    is_user = db.query(User).filter(
        func.lower(User.email) == func.lower(newuser.email)
    ).first()
    
    if(is_user):
        raise HTTPException(status_code=401, detail="Email Already Used")
    
    hash_password = get_password_hash(newuser.password)
    
    new_user = User(
        full_name=newuser.full_name,
        email = newuser.email,
        password_hash = hash_password,
        role = UserRole
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def login(userdata:UserLogin,db:Session):
    print(userdata)
    
    user = db.query(User).filter(
        func.lower(User.email) == func.lower(userdata.email)
    ).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User Not Found")

    if not verify_password(userdata.password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Wrong Password!")
        
    expiry_time = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print("Type of user id: ",type(user.id))
    token = jwt.encode({'_id':str(user.id), 'full_name':user.full_name, 'exp':expiry_time},key=SECRET_KEY,algorithm=ALGORITHM)
    
    return {'token':token}

def is_authenticated(request:Request, db :Session):
    try:
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Not Found!!")
        token = token.split(" ")[-1]
        
        data = jwt.decode(token,key=SECRET_KEY,algorithms=ALGORITHM)
        user_id = data.get("_id") 
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token!!")
        
        
        return user
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You Are Not Authorized!!")


def require_roles(allowed_roles: list, request: Request, db: Session):
    """
    Flexible role-based authorization
    Args:
        allowed_roles: List of roles that can access the resource
        request: FastAPI request object
        db: Database session
    Returns:
        User object if authorized
    Raises:
        HTTPException if not authorized
    """
    user = is_authenticated(request, db)
    
    # Convert roles to lowercase for case-insensitive comparison
    user_role = user.role.lower() if user.role else ""
    allowed_roles_lower = [role.lower() for role in allowed_roles]
  
    if user_role not in allowed_roles_lower:
        roles_str = ", ".join(allowed_roles)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Access denied! Required roles: {roles_str}. Your role: {user.role}"
        )
    return user

