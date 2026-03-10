from flask import Blueprint, render_template, flash
from database.connection import query

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    try:
        # Fetch all enquiries, ordered by most recent
        enquiries = query("SELECT * FROM enquiries ORDER BY submitted_at DESC")
        return render_template('admin/dashboard.html', enquiries=enquiries)
    except Exception as e:
        flash(f"Error loading dashboard: {e}", "danger")
        return render_template('admin/dashboard.html', enquiries=[])
