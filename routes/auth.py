from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database.connection import query

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to respective dashboard
    if 'user_id' in session:
        user_role = session.get('role')
        if user_role == 'student':
            return redirect(url_for('student.dashboard'))
        elif user_role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif user_role == 'parent':
            return redirect(url_for('parent.dashboard'))
        elif user_role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')

        if not role or not username or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.login', role=role))

        # Check DB for user matching role and username
        db_query = "SELECT id, role, username, password_hash, is_active FROM users WHERE username = %s AND role = %s"
        try:
            user = query(db_query, (username, role), fetch_one=True)
            
            if user and check_password_hash(user['password_hash'], password):
                if not user['is_active']:
                    flash('Your account has been deactivated. Please contact administration.', 'warning')
                    return redirect(url_for('auth.login', role=role))

                # Prevent session fixation
                session.clear()
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['username'] = user['username']

                flash(f"Welcome back, {user['username']}!", 'success')
                
                if user['role'] == 'student':
                    return redirect(url_for('student.dashboard'))
                elif user['role'] == 'teacher':
                    return redirect(url_for('teacher.dashboard'))
                elif user['role'] == 'parent':
                    return redirect(url_for('parent.dashboard'))
                elif user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                
                return redirect(url_for('public.index'))
            else:
                flash("Invalid username or password. Please try again.", "danger")
                return redirect(url_for('auth.login', role=role))
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash("An error occurred during login. Please try again later.", "danger")
            return redirect(url_for('auth.login', role=role))

    # GET request - serve login page
    selected_role = request.args.get('role', 'student') 
    return render_template('auth/login.html', selected_role=selected_role)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('public.index'))
