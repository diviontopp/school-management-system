from flask import Blueprint, render_template

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/dashboard')
def dashboard():
    return render_template('parent/dashboard.html')
