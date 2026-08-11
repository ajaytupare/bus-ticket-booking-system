from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models.user_model import UserModel

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('role') != 'admin':
            flash('Unauthorized access. Admin privileges required.', 'danger')
            return redirect(url_for('user.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('user.index'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name or not email or not phone or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        existing_user = UserModel.get_by_email(email)
        if existing_user:
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/register.html')

        try:
            UserModel.create_user(name, email, phone, password, role='user')
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error registering user: {str(e)}', 'danger')
            return render_template('auth/register.html')

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('user.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')

        user = UserModel.get_by_email(email)
        if not user or not UserModel.verify_password(user['password'], password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        # Session Setup
        session['user_id'] = user['id']
        session['name'] = user['name']
        session['email'] = user['email']
        session['role'] = user['role']

        flash(f'Welcome back, {user["name"]}!', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)

        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.index'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('user.index'))
