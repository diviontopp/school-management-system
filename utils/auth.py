from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    """
    Decorator to ensure the user is logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            # Assuming 'auth.login' is the endpoint for the login route
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """
    Decorator to ensure the logged-in user has one of the required roles.
    Example: @role_required('admin', 'teacher')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            user_role = session.get('role')
            if user_role not in roles:
                flash('You do not have permission to access that page.', 'danger')
                # Redirect to their specific dashboard based on role, or public home
                if user_role == 'student':
                    return redirect(url_for('student.dashboard'))
                elif user_role == 'teacher':
                    return redirect(url_for('teacher.dashboard'))
                elif user_role == 'parent':
                    return redirect(url_for('parent.dashboard'))
                elif user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('public.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
