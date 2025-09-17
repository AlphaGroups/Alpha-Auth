# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
# from sqlalchemy.orm import Session
# from database import get_db
# from models import User, RoleEnum
# # from utils import hash_password
# from utils.security import hash_password
# import csv

# router = APIRouter(prefix="/students", tags=["Students"])


# @router.post("/import")
# async def import_students(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     # Check file type
#     if not file.filename.endswith(".csv"):
#         raise HTTPException(status_code=400, detail="Only CSV files are allowed")

#     # Read file
#     content = await file.read()
#     decoded = content.decode("utf-8").splitlines()
#     reader = csv.DictReader(decoded)

#     students = []
#     for row in reader:
#         first_name = row["first_name"].strip()
#         last_name = row.get("last_name", "").strip()
#         birth_year = row["birth_year"].strip()
#         student_id = row["student_id"].strip()

#         # Auto-generate email from student_id
#         email = f"{student_id}@college.edu"

#         # Auto-generate password as firstname+birthyear
#         password = f"{first_name.lower()}{birth_year}"
#         hashed_password = hash_password(password)

#         # Create student record in users table
#         student = User(
#             name=f"{first_name} {last_name}".strip(),
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#             hashed_password=hashed_password,
#             role=RoleEnum.student,
#         )
#         students.append(student)

#     # Bulk insert
#     db.bulk_save_objects(students)
#     db.commit()

#     return {"message": f"{len(students)} students imported successfully"}


from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User, RoleEnum
from utils.security import hash_password
import csv
from typing import List, Dict, Any

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/import")
async def import_students(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Check file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    # Read file
    content = await file.read()
    decoded = content.decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)

    students = []
    duplicates = []
    errors = []
    processed_emails = set()  # Track emails within the current import
    processed_student_ids = set()  # Track student IDs within the current import

    for row_num, row in enumerate(reader, start=2):  # Start at 2 since row 1 is header
        try:
            first_name = row["first_name"].strip()
            last_name = row.get("last_name", "").strip()
            birth_year = row["birth_year"].strip()
            student_id = row["student_id"].strip()

            # Validate required fields
            if not all([first_name, birth_year, student_id]):
                errors.append(f"Row {row_num}: Missing required fields (first_name, birth_year, student_id)")
                continue

            # Validate birth year is numeric
            try:
                int(birth_year)
            except ValueError:
                errors.append(f"Row {row_num}: Invalid birth_year '{birth_year}'")
                continue

            # Auto-generate email from student_id
            email = f"{student_id}@college.edu"

            # Check for duplicates within the current import
            if email in processed_emails:
                duplicates.append(f"Row {row_num}: Duplicate email '{email}' within import file")
                continue
            
            if student_id in processed_student_ids:
                duplicates.append(f"Row {row_num}: Duplicate student_id '{student_id}' within import file")
                continue

            # Check for existing records in database
            existing_user_by_email = db.query(User).filter(User.email == email).first()
            if existing_user_by_email:
                duplicates.append(f"Row {row_num}: Email '{email}' already exists in database")
                continue

            # Auto-generate password as firstname+birthyear
            password = f"{first_name.lower()}{birth_year}"
            hashed_password = hash_password(password)

            # Create student record
            student = User(
                name=f"{first_name} {last_name}".strip(),
                first_name=first_name,
                last_name=last_name,
                email=email,
                hashed_password=hashed_password,
                role=RoleEnum.student,
            )
            students.append(student)
            processed_emails.add(email)
            processed_student_ids.add(student_id)

        except KeyError as e:
            errors.append(f"Row {row_num}: Missing column {e}")
        except Exception as e:
            errors.append(f"Row {row_num}: Unexpected error - {str(e)}")

    # Attempt bulk insert
    successful_imports = 0
    if students:
        try:
            db.bulk_save_objects(students)
            db.commit()
            successful_imports = len(students)
        except IntegrityError as e:
            db.rollback()
            # If bulk insert fails, try individual inserts to identify specific duplicates
            for student in students:
                try:
                    db.add(student)
                    db.commit()
                    successful_imports += 1
                except IntegrityError:
                    db.rollback()
                    duplicates.append(f"Database constraint violation for email: {student.email}")
                except Exception as e:
                    db.rollback()
                    errors.append(f"Failed to insert student {student.email}: {str(e)}")

    # Prepare response
    response = {
        "message": f"{successful_imports} students imported successfully",
        "successful_imports": successful_imports,
        "total_processed": len(students) + len(duplicates) + len(errors),
    }

    if duplicates:
        response["duplicates"] = duplicates
        response["duplicate_count"] = len(duplicates)

    if errors:
        response["errors"] = errors
        response["error_count"] = len(errors)

    return response


@router.post("/import-with-update")
async def import_students_with_update(
    file: UploadFile = File(...), 
    update_existing: bool = False,
    db: Session = Depends(get_db)
):
    """
    Import students with option to update existing records
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    decoded = content.decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)

    created = 0
    updated = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            first_name = row["first_name"].strip()
            last_name = row.get("last_name", "").strip()
            birth_year = row["birth_year"].strip()
            student_id = row["student_id"].strip()

            if not all([first_name, birth_year, student_id]):
                errors.append(f"Row {row_num}: Missing required fields")
                continue

            try:
                int(birth_year)
            except ValueError:
                errors.append(f"Row {row_num}: Invalid birth_year '{birth_year}'")
                continue

            email = f"{student_id}@college.edu"
            password = f"{first_name.lower()}{birth_year}"
            hashed_password = hash_password(password)

            # Check if student exists
            existing_student = db.query(User).filter(User.email == email).first()

            if existing_student:
                if update_existing:
                    # Update existing record
                    existing_student.name = f"{first_name} {last_name}".strip()
                    existing_student.first_name = first_name
                    existing_student.last_name = last_name
                    existing_student.hashed_password = hashed_password
                    updated += 1
                else:
                    # Skip existing record
                    skipped += 1
            else:
                # Create new record
                student = User(
                    name=f"{first_name} {last_name}".strip(),
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    hashed_password=hashed_password,
                    role=RoleEnum.student,
                )
                db.add(student)
                created += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit failed: {str(e)}")

    response = {
        "message": f"Import completed: {created} created, {updated} updated, {skipped} skipped",
        "created": created,
        "updated": updated,
        "skipped": skipped,
    }

    if errors:
        response["errors"] = errors
        response["error_count"] = len(errors)

    return response