from sqlalchemy.orm import Session
from models import User, RoleEnum, Teacher
from utils.security import hash_password
from app.schemas.teacher import TeacherCreate
from utils.email_service import send_email


def create_teacher(
    db: Session,
    teacher_data: TeacherCreate,
    college_id: int,
    created_by_admin_id: int | None = None
):
    """
    Create a new Teacher user and record in teachers table.
    - Prevents duplicate emails across all users.
    - Automatically hashes password.
    - Binds teacher to the correct college.
    """
    # 🔍 Ensure email is not already used by any user
    existing_user = db.query(User).filter(User.email == teacher_data.email).first()
    if existing_user:
        raise ValueError("A user with this email already exists")

    # ✅ Create a User entry for teacher (with RoleEnum.teacher)
    hashed_password = hash_password(teacher_data.password)
    user = User(
        name=teacher_data.full_name,  # name field in User table
        first_name=teacher_data.full_name.split()[0],
        last_name=" ".join(teacher_data.full_name.split()[1:]) if len(teacher_data.full_name.split()) > 1 else None,
        email=teacher_data.email,
        mobile=teacher_data.mobile,
        hashed_password=hashed_password,
        role=RoleEnum.teacher,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ Create the Teacher entry linked to User
    teacher = Teacher(
        user_id=user.id,
        full_name=teacher_data.full_name,
        email=teacher_data.email,
        mobile=teacher_data.mobile,
        hashed_password=hashed_password,
        college_id=college_id,
        created_by_admin_id=created_by_admin_id,
        subject=teacher_data.subject,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    # Send welcome email to the teacher
    try:
        # Extract first name from full name for personalization
        parts = teacher_data.full_name.strip().split()
        first_name = parts[0] if parts else teacher_data.full_name

        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Alpha Groups, {first_name}!</h2>
            <p>Your teacher account has been successfully created.</p>
            <p><strong>Account Details:</strong></p>
            <ul>
                <li><strong>Email:</strong> {teacher_data.email}</li>
                <li><strong>Role:</strong> Teacher</li>
                <li><strong>Subject:</strong> {teacher_data.subject}</li>
                <li><strong>Temporary Password:</strong> {teacher_data.password}</li>
            </ul>
            <p>Please change your password after your first login for security.</p>
            <p>Thank you for using Alpha Groups platform!</p>
        </body>
        </html>
        """
        
        plain_text = f"""
        Welcome to Alpha Groups, {first_name}!
        
        Your teacher account has been successfully created.
        
        Account Details:
        - Email: {teacher_data.email}
        - Role: Teacher
        - Subject: {teacher_data.subject}
        - Temporary Password: {teacher_data.password}
        
        Please change your password after your first login for security.
        Thank you for using Alpha Groups platform!
        """
        
        success = send_email(
            to_email=teacher_data.email,
            subject="Welcome - Teacher Account Created",
            html=html_content,
            plain_text=plain_text
        )
        
        if success:
            print(f"✅ Welcome email sent to teacher: {teacher_data.email}")
        else:
            print(f"❌ Failed to send welcome email to teacher: {teacher_data.email}")
            
    except Exception as e:
        print(f"❌ Error sending welcome email: {str(e)}")

    return teacher
