from flask import Blueprint, render_template
from utils.auth import login_required

library_bp = Blueprint('library', __name__)

@library_bp.route('/catalogue')
@login_required
def catalogue():
    return render_template('library/catalogue.html')
