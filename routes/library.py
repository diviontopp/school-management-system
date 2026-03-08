from flask import Blueprint, render_template

library_bp = Blueprint('library', __name__)

@library_bp.route('/catalogue')
def catalogue():
    return render_template('library/catalogue.html')
