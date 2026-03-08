from flask import Blueprint, render_template

clubs_bp = Blueprint('clubs', __name__)

@clubs_bp.route('/')
def listing():
    return render_template('clubs/listing.html')
