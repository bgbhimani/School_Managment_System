from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import models
from app.api.v1.endpoints import auth, admin

app = FastAPI(title="School Management System Backend")

# # Create database tables on startup
# @app.on_event("startup")
# def create_tables():
#     print("Creating database tables...")
#     Base.metadata.create_all(bind=engine)
#     print("Database tables created successfully!")

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.auth_router, prefix='/auth', tags=['auth'])
app.include_router(admin.admin_router, prefix='/admin', tags=['admin'])

@app.get("/")
def read_root():
    return {"status": "Helllo Bachchooooo!!!!"}