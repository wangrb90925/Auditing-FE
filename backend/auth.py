from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from database import User, db

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user or not user.is_admin():
            return {'error': 'Admin access required'}, 403
        return fn(*args, **kwargs)
    return wrapper

def auditor_required(fn):
    """Decorator to require auditor role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user or not (user.is_auditor() or user.is_admin()):
            return {'error': 'Auditor access required'}, 403
        return fn(*args, **kwargs)
    return wrapper

def create_user(username, email, password, first_name, last_name, role='auditor'):
    """Create a new user"""
    try:
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def authenticate_user(username, password):
    """Authenticate user and return user object if valid"""
    try:
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            return user, None
        else:
            return None, "Invalid credentials"
            
    except Exception as e:
        return None, str(e)

def get_user_by_id(user_id):
    """Get user by ID"""
    return User.query.get(user_id)

def get_all_users():
    """Get all users (admin only)"""
    return User.query.all()

def update_user(user_id, **kwargs):
    """Update user information"""
    try:
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email', 'username', 'is_active', 'role']
        for field, value in kwargs.items():
            if field in allowed_fields:
                # Check for unique constraints
                if field == 'username' and value != user.username:
                    existing_user = User.query.filter_by(username=value).first()
                    if existing_user and existing_user.id != user_id:
                        return None, "Username already exists"
                elif field == 'email' and value != user.email:
                    existing_user = User.query.filter_by(email=value).first()
                    if existing_user and existing_user.id != user_id:
                        return None, "Email already exists"
                elif field == 'role':
                    # Validate role value
                    if value not in ['admin', 'auditor']:
                        return None, "Invalid role. Must be 'admin' or 'auditor'"
                
                setattr(user, field, value)
        
        db.session.commit()
        return user, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def change_user_password(user_id, current_password, new_password):
    """Change user password"""
    try:
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        
        # Verify current password
        if not user.check_password(current_password):
            return None, "Current password is incorrect"
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        return user, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def change_user_role(user_id, new_role):
    """Change user role (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        
        if new_role not in ['admin', 'auditor']:
            return None, "Invalid role"
        
        user.role = new_role
        db.session.commit()
        return user, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def create_default_admin():
    """Create default admin user if no users exist"""
    try:
        if User.query.count() == 0:
            admin_user, error = create_user(
                username='admin',
                email='admin@auditengine.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            
            if admin_user:
                print("[SUCCESS] Default admin user created:")
                print("   Username: admin")
                print("   Password: admin123")
                print("   Please change the password after first login!")
            else:
                print(f"[ERROR] Failed to create default admin: {error}")
                
    except Exception as e:
        print(f"[ERROR] Error creating default admin: {e}")


