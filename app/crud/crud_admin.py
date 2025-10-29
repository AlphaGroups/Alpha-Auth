from sqlalchemy.orm import Session
from models import Admin, College, User, RoleEnum
from utils.security import hash_password
from app.schemas.College_Admin import AdminCreate
from utils.email_service import send_email

def create_admin(db: Session, admin_data: AdminCreate):
    # Check if college exists
    college = db.query(College).filter(College.name == admin_data.college_name).first()
    if not college:
        college = College(name=admin_data.college_name)
        db.add(college)
        db.commit()
        db.refresh(college)

    # Check if user/email already exists
    existing_user = db.query(User).filter(User.email == admin_data.email).first()
    if existing_user:
        raise ValueError("Admin with this email already exists")

    # Create User first (so we can link to Admin)
    hashed_password = hash_password(admin_data.password)
    new_user = User(
        name=admin_data.full_name,
        email=admin_data.email,
        mobile=admin_data.mobile,
        hashed_password=hashed_password,
        role=RoleEnum.admin,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Now create Admin and link user_id
    new_admin = Admin(
        user_id=new_user.id,      # ✅ link dynamic user id
        full_name=admin_data.full_name,
        email=admin_data.email,
        phone=admin_data.mobile,
        college_id=college.id,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    # Send welcome email to the admin
    try:
        # Extract first name from full name for personalization
        parts = admin_data.full_name.strip().split()
        first_name = parts[0] if parts else admin_data.full_name

        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Alpha Groups, {first_name}!</h2>
            <p>Your admin account has been successfully created.</p>
            <p><strong>Account Details:</strong></p>
            <ul>
                <li><strong>Email:</strong> {admin_data.email}</li>
                <li><strong>Role:</strong> Admin</li>
                <li><strong>College:</strong> {admin_data.college_name}</li>
                <li><strong>Temporary Password:</strong> {admin_data.password}</li>
            </ul>
            <p>Please change your password after your first login for security.</p>
            <p>Thank you for using Alpha Groups platform!</p>
        </body>
        </html>
        """
        
        plain_text = f"""
        Welcome to Alpha Groups, {first_name}!
        
        Your admin account has been successfully created.
        
        Account Details:
        - Email: {admin_data.email}
        - Role: Admin
        - College: {admin_data.college_name}
        - Temporary Password: {admin_data.password}
        
        Please change your password after your first login for security.
        Thank you for using Alpha Groups platform!
        """
        
        success = send_email(
            to_email=admin_data.email,
            subject="Welcome - Admin Account Created",
            html=html_content,
            plain_text=plain_text
        )
        
        if success:
            print(f"✅ Welcome email sent to admin: {admin_data.email}")
        else:
            print(f"❌ Failed to send welcome email to admin: {admin_data.email}")
            
    except Exception as e:
        print(f"❌ Error sending welcome email: {str(e)}")

    return new_admin


def get_all_admins(db: Session):
    """
    Fetch all admins from the database with their related college.
    Returns a list of Admin objects.
    """
    return db.query(Admin).all()
