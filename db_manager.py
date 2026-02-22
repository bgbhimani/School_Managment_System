"""
Database manager for School Management System.
Provides utilities for database initialization, seeding, and management.
"""

from sqlalchemy import text
from app.database import engine, SessionLocal, Base
from app.models.models import (
    User, Class, Subject, Teacher, Student, TeacherClass, 
    Notice, AttendanceSession, AttendanceRecord, Test, TestResult,
    UserRole
)
import uuid
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def create_tables(self):
        """Create all database tables."""
        print("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database tables created successfully!")
        self._print_table_info()

    def drop_tables(self):
        """Drop all database tables. Use with caution!"""
        print("⚠️  Dropping all database tables...")
        Base.metadata.drop_all(bind=self.engine)
        print("✅ All tables dropped.")

    def reset_database(self):
        """Drop and recreate all tables. Use with caution!"""
        print("🔄 Resetting database...")
        self.drop_tables()
        self.create_tables()
        print("✅ Database reset complete.")

    def check_connection(self):
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✅ Database connection successful!")
                return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def _print_table_info(self):
        """Print information about created tables."""
        print("\n📋 Created tables:")
        for table_name in Base.metadata.tables.keys():
            table = Base.metadata.tables[table_name]
            column_count = len(table.columns)
            print(f"  • {table_name} ({column_count} columns)")

    def seed_basic_data(self):
        """Seed the database with basic required data."""
        print("🌱 Seeding basic data...")
        
        db = self.SessionLocal()
        try:
            # Create basic subjects
            subjects_data = [
                "Mathematics",
                "Science", 
                "English",
                "Hindi",
                "Social Studies",
                "Computer Science"
            ]
            
            existing_subjects = db.query(Subject).count()
            if existing_subjects == 0:
                subjects = []
                for subject_name in subjects_data:
                    subject = Subject(
                        id=uuid.uuid4(),
                        name=subject_name
                    )
                    subjects.append(subject)
                
                db.add_all(subjects)
                print(f"  ✅ Created {len(subjects)} subjects")
            else:
                print(f"  ℹ️  Subjects already exist ({existing_subjects} found)")

            # Create basic classes
            classes_data = [
                (1, "A"), (1, "B"),
                (2, "A"), (2, "B"), 
                (3, "A"), (3, "B"),
                (4, "A"), (4, "B"),
                (5, "A"), (5, "B")
            ]
            
            existing_classes = db.query(Class).count()
            if existing_classes == 0:
                classes = []
                for standard, section in classes_data:
                    class_obj = Class(
                        id=uuid.uuid4(),
                        standard=standard,
                        section=section
                    )
                    classes.append(class_obj)
                
                db.add_all(classes)
                print(f"  ✅ Created {len(classes)} classes")
            else:
                print(f"  ℹ️  Classes already exist ({existing_classes} found)")

            # Create admin user
            existing_admin = db.query(User).filter(User.role == UserRole.admin).first()
            if not existing_admin:
                admin_user = User(
                    id=uuid.uuid4(),
                    full_name="System Administrator",
                    email="admin@school.com",
                    password_hash="$2b$12$placeholder_hash",  # In real app, hash the password
                    role=UserRole.admin
                )
                db.add(admin_user)
                print("  ✅ Created admin user (email: admin@school.com)")
            else:
                print("  ℹ️  Admin user already exists")

            db.commit()
            print("✅ Basic data seeding completed!")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding data: {e}")
            raise
        finally:
            db.close()

    def get_table_counts(self):
        """Get record counts for all tables."""
        db = self.SessionLocal()
        try:
            models_map = {
                'users': User,
                'classes': Class,
                'subjects': Subject,
                'teachers': Teacher,
                'students': Student,
                'teacher_classes': TeacherClass,
                'notices': Notice,
                'attendance_sessions': AttendanceSession,
                'attendance_records': AttendanceRecord,
                'tests': Test,
                'test_results': TestResult
            }
            
            print("\n📊 Table record counts:")
            for table_name, model in models_map.items():
                count = db.query(model).count()
                print(f"  • {table_name}: {count}")
                
        except Exception as e:
            print(f"❌ Error getting table counts: {e}")
        finally:
            db.close()


def main():
    """Main function for command line usage."""
    import sys
    
    db_manager = DatabaseManager()
    
    if len(sys.argv) < 2:
        print("Usage: python db_manager.py [command]")
        print("\nAvailable commands:")
        print("  create    - Create all tables")
        print("  drop      - Drop all tables")
        print("  reset     - Drop and recreate all tables")
        print("  seed      - Seed basic data")
        print("  check     - Check database connection")
        print("  counts    - Show record counts")
        print("  init      - Create tables and seed basic data")
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        db_manager.create_tables()
    elif command == "drop":
        db_manager.drop_tables()
    elif command == "reset":
        db_manager.reset_database()
    elif command == "seed":
        db_manager.seed_basic_data()
    elif command == "check":
        db_manager.check_connection()
    elif command == "counts":
        db_manager.get_table_counts()
    elif command == "init":
        if db_manager.check_connection():
            db_manager.create_tables()
            db_manager.seed_basic_data()
            db_manager.get_table_counts()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()