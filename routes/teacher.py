from flask import Blueprint, render_template
from utils.auth import login_required, role_required

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
@login_required
@role_required('teacher')
def dashboard():
    return render_template('teacher/dashboard.html')
