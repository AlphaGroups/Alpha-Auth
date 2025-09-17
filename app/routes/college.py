# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database import get_db
# import models, schemas

# router = APIRouter(prefix="/colleges", tags=["Colleges"])

# @router.post("/", response_model=schemas.CollegeOut)
# def create_college(college: schemas.CollegeCreate, db: Session = Depends(get_db)):
#     existing = db.query(models.College).filter(models.College.name == college.name).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="College already exists")
#     new_college = models.College(name=college.name)
#     db.add(new_college)
#     db.commit()
#     db.refresh(new_college)
#     return new_college

# @router.get("/", response_model=list[schemas.CollegeOut])
# def list_colleges(db: Session = Depends(get_db)):
#     return db.query(models.College).all()


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from app.schemas.College_Admin import CollegeCreate, CollegeOut


router = APIRouter(prefix="/colleges", tags=["Colleges"])

@router.post("/", response_model=CollegeOut)
def create_college(college: CollegeCreate, db: Session = Depends(get_db)):
    existing = db.query(models.College).filter(models.College.name == college.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="College already exists")
    new_college = models.College(name=college.name)
    db.add(new_college)
    db.commit()
    db.refresh(new_college)
    return new_college

@router.get("/", response_model=list[CollegeOut])
def list_colleges(db: Session = Depends(get_db)):
    return db.query(models.College).all()
