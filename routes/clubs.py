from flask import Blueprint, render_template
from utils.auth import login_required

clubs_bp = Blueprint('clubs', __name__)

@clubs_bp.route('/')
@login_required
def listing():
    return render_template('clubs/listing.html')
