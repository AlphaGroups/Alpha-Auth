from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Student, RoleEnum, Admin, User
from utils.security import hash_password, get_current_user, require_role
import csv

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/import")
async def import_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import students into the `students` table.
    Admin → auto-assigns their college_id
    Superadmin → must provide college_id in CSV
    """
    # Validate role
    if current_user.role not in [RoleEnum.admin, RoleEnum.superadmin]:
        raise HTTPException(status_code=403, detail="Only admins can import students")

    # Ensure admin has a valid college_id
    if current_user.role == RoleEnum.admin:
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin:
            raise HTTPException(status_code=400, detail="Admin record not found")
        college_id = admin.college_id
    else:
        college_id = None  # superadmin must provide in CSV

    # Check file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    # Read CSV file
    content = await file.read()
    decoded = content.decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)

    students = []
    duplicates = []
    errors = []
    processed_emails = set()
    processed_ids = set()

    for row_num, row in enumerate(reader, start=2):
        try:
            first_name = row["first_name"].strip()
            last_name = row.get("last_name", "").strip()
            birth_year = row["birth_year"].strip()
            student_id = row["student_id"].strip()

            # ✅ If superadmin → require college_id in CSV
            row_college_id = row.get("college_id")
            if current_user.role == RoleEnum.superadmin:
                if not row_college_id:
                    errors.append(f"Row {row_num}: Superadmin must provide college_id")
                    continue
                try:
                    row_college_id = int(row_college_id)
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid college_id '{row_college_id}'")
                    continue
                assigned_college_id = row_college_id
            else:
                assigned_college_id = college_id

            # Validate required fields
            if not all([first_name, birth_year, student_id, assigned_college_id]):
                errors.append(f"Row {row_num}: Missing required fields")
                continue

            try:
                int(birth_year)
            except ValueError:
                errors.append(f"Row {row_num}: Invalid birth_year '{birth_year}'")
                continue

            # Generate email
            email = f"{student_id}@college.edu"

            # Prevent duplicates in this batch
            if email in processed_emails or student_id in processed_ids:
                duplicates.append(f"Row {row_num}: Duplicate student '{student_id}' or '{email}' in CSV")
                continue

            # Prevent duplicates in DB
            existing = db.query(Student).filter(
                (Student.email == email) | (Student.student_id == student_id)
            ).first()
            if existing:
                duplicates.append(f"Row {row_num}: Student with email '{email}' or ID '{student_id}' already exists")
                continue

            # Password = firstname + birthyear
            password = f"{first_name.lower()}{birth_year}"
            hashed_password = hash_password(password)

            student = Student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                birth_year=int(birth_year),
                email=email,
                hashed_password=hashed_password,
                college_id=assigned_college_id,
                created_by_teacher_id=None  # if teacher uploads, we can set this later
            )

            students.append(student)
            processed_emails.add(email)
            processed_ids.add(student_id)

        except KeyError as e:
            errors.append(f"Row {row_num}: Missing column {e}")
        except Exception as e:
            errors.append(f"Row {row_num}: Unexpected error - {str(e)}")

    # Bulk save
    successful_imports = 0
    if students:
        try:
            db.bulk_save_objects(students)
            db.commit()
            successful_imports = len(students)
        except IntegrityError:
            db.rollback()
            # fallback: insert one by one
            for student in students:
                try:
                    db.add(student)
                    db.commit()
                    successful_imports += 1
                except IntegrityError:
                    db.rollback()
                    duplicates.append(f"Duplicate in DB: {student.student_id}/{student.email}")
                except Exception as e:
                    db.rollback()
                    errors.append(f"Failed insert: {student.student_id} → {str(e)}")

    response = {
        "message": f"{successful_imports} students imported successfully",
        "successful_imports": successful_imports,
        "total_processed": len(students) + len(duplicates) + len(errors)
    }
    if duplicates:
        response["duplicates"] = duplicates
    if errors:
        response["errors"] = errors

    return response
