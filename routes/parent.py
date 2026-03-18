from flask import Blueprint, render_template
from utils.auth import login_required, role_required

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/dashboard')
@login_required
@role_required('parent')
def dashboard():
    return render_template('parent/dashboard.html')
