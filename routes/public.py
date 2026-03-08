from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.connection import query

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    return render_template('public/index.html')

@public_bp.route('/admissions')
def admissions():
    return render_template('public/admissions.html')

@public_bp.route('/faculty')
def faculty():
    return render_template('public/faculty.html')

@public_bp.route('/gallery')
def gallery():
    return render_template('public/gallery.html')

@public_bp.route('/contact')
def contact():
    return render_template('public/contact.html')

@public_bp.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    parent_name = request.form.get('parent_name')
    student_name = request.form.get('student_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    grade = request.form.get('grade')
    dob = request.form.get('dob')
    
    # Simple validation
    if not (parent_name and student_name and email and phone and grade and dob):
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('public.admissions'))
        
    try:
        # Construct message content from student name and DOB
        message = f"Inquiry for student {student_name} (DOB: {dob})"
        
        # Using the existing 'enquiries' table in the schema
        sql = """
            INSERT INTO enquiries (parent_name, email, phone, child_grade, message)
            VALUES (%s, %s, %s, %s, %s)
        """
        query(sql, (parent_name, email, phone, grade, message), commit=True)
        
        flash('Your enquiry has been submitted successfully! Our admissions team will reach out soon.', 'success')
    except Exception as e:
        flash(f'An error occurred while submitting your enquiry: {e}', 'danger')
        print(f"Error submitting enquiry: {e}")
        
    return redirect(url_for('public.admissions'))

@public_bp.route('/submit-contact', methods=['POST'])
def submit_contact():
    parent_name = request.form.get('parent_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    subject = request.form.get('subject', 'General Inquiry')
    user_message = request.form.get('message')
    
    # We will format the subject line directly into the message block to persist meaning alongside the primary data since child_grade doesn't map directly from general contact.
    compiled_message = f"[{subject}] {user_message}"
    
    if not (parent_name and email and user_message):
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('public.contact'))
        
    try:
        sql = """
            INSERT INTO enquiries (parent_name, email, phone, child_grade, message)
            VALUES (%s, %s, %s, %s, %s)
        """
        # Pass None as the grade for a general inquiry
        query(sql, (parent_name, email, phone, None, compiled_message), commit=True)
        flash('Your message has been sent successfully. We will get back to you shortly!', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        print(f"Error submitting contact: {e}")
        
    return redirect(url_for('public.contact'))
