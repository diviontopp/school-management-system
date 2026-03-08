from flask import Blueprint, render_template

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
def dashboard():
    return render_template('teacher/dashboard.html')
