from flask import Blueprint, render_template, flash, redirect, url_for
from database.connection import query, initialize_database
from utils.auth import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/force-init')
@role_required('admin')
def force_init():
    """Manual trigger to force database initialization."""
    try:
        initialize_database()
        flash('Database initialization triggered! Check logs for details.', 'success')
    except Exception as e:
        flash(f'Error triggering init: {e}', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    try:
        # Fetch all enquiries, ordered by most recent
        enquiries = query("SELECT * FROM enquiries ORDER BY submitted_at DESC")
        return render_template('admin/dashboard.html', enquiries=enquiries)
    except Exception as e:
        flash(f"Error loading dashboard: {e}", "danger")
        return render_template('admin/dashboard.html', enquiries=[])
