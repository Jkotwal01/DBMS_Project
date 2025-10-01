from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
import models, schemas
import crud


def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Create a faculty user
        try:
            fac_user = crud.create_user(db, schemas.UserCreate(
                name="Alice Faculty",
                email="alice.faculty@example.com",
                password="password123",
                role="Faculty",
                department="CSE"
            ))
            crud.create_faculty_profile(db, fac_user.user_id, schemas.FacultyCreate(designation="Professor", dept="CSE"))
        except Exception:
            pass

        # Create a student user
        try:
            stu_user = crud.create_user(db, schemas.UserCreate(
                name="Bob Student",
                email="bob.student@example.com",
                password="password123",
                role="Student",
                department="CSE"
            ))
            crud.create_student_profile(db, stu_user.user_id, schemas.StudentCreate(
                roll_no="CSE001",
                class_name="CSE-A",
                year=2,
                section="A"
            ))
        except Exception:
            pass

        # Create a sample subject assigned to faculty
        subj = crud.create_subject(db, schemas.SubjectCreate(subject_name="DBMS", faculty_id=1, semester=3))

    finally:
        db.close()


if __name__ == "__main__":
    seed()

