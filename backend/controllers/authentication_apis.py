import re
from datetime import datetime
from flask import jsonify, make_response, request
from flask_restful import Resource
from flask_security import auth_token_required, current_user, login_user, logout_user, utils
from sqlalchemy.exc import IntegrityError
from controllers.database import db
from controllers.models import Company, Role, Student
from controllers.user_datastore import user_datastore
EMAIL_PATTERN = re.compile('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')

def validate_email(email):
    """Return True when the supplied value is a valid email address."""
    return bool(email and EMAIL_PATTERN.fullmatch(email))

def validate_password(password):
    """Validate the password rules used during registration and password changes."""
    if not password or len(password) < 8:
        return (False, 'Password must be at least 8 characters long.')
    if len(password) > 100:
        return (False, 'Password cannot be longer than 100 characters.')
    if not any((character.isupper() for character in password)):
        return (False, 'Password must contain at least one uppercase letter.')
    if not any((character.islower() for character in password)):
        return (False, 'Password must contain at least one lowercase letter.')
    if not any((character.isdigit() for character in password)):
        return (False, 'Password must contain at least one number.')
    return (True, None)

def clean_text(value):
    """Trim string input while leaving non-string values unchanged."""
    return value.strip() if isinstance(value, str) else value

def serialize_user(user):
    """Build the common authenticated-user response."""
    profile = user.get_profile()
    return {'id': user.id, 'email': user.email, 'role': user.get_role_name(), 'profile': profile.to_dict() if profile and hasattr(profile, 'to_dict') else {}}

class CheckEmailAPI(Resource):
    """Check whether an email address is available for registration."""

    def post(self):
        data = request.get_json(silent=True) or {}
        email = clean_text(data.get('email', '')).lower()
        if not validate_email(email):
            return make_response(jsonify({'message': 'Enter a valid email address.'}), 400)
        user = user_datastore.find_user(email=email)
        return make_response(jsonify({'available': user is None}), 200)

class RegisterAPI(Resource):
    """Register a student or company account."""

    def post(self):
        data = request.get_json(silent=True) or {}
        email = clean_text(data.get('email', '')).lower()
        password = data.get('password', '')
        role_name = clean_text(data.get('role', '')).lower()
        profile_data = data.get('profile')
        if not isinstance(profile_data, dict):
            return make_response(jsonify({'message': 'Profile data is required.'}), 400)
        if not email or not password or (not role_name):
            return make_response(jsonify({'message': 'Email, password and role are required.'}), 400)
        if not validate_email(email):
            return make_response(jsonify({'message': 'Enter a valid email address.'}), 400)
        password_valid, password_error = validate_password(password)
        if not password_valid:
            return make_response(jsonify({'message': password_error}), 400)
        if role_name not in {Role.STUDENT, Role.COMPANY}:
            return make_response(jsonify({'message': 'Role must be either "student" or "company".'}), 400)
        if user_datastore.find_user(email=email):
            return make_response(jsonify({'message': 'Email is already registered.'}), 409)
        role = user_datastore.find_role(role_name)
        if not role:
            return make_response(jsonify({'message': 'Application roles are not initialized. Restart the backend and try again.'}), 500)
        try:
            user = user_datastore.create_user(email=email, password=utils.hash_password(password), active=True)
            user_datastore.add_role_to_user(user, role)
            db.session.flush()
            if role_name == Role.STUDENT:
                message = self._create_student(user, profile_data)
            else:
                message = self._create_company(user, profile_data)
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            return make_response(jsonify({'message': str(error)}), 400)
        except IntegrityError:
            db.session.rollback()
            return make_response(
                jsonify(
                    {
                        "message": (
                            "Registration could not be completed because "
                            "the submitted account data conflicts with an "
                            "existing record."
                        )
                    }
                ),
                409,
            )
        return make_response(jsonify({'message': message, 'user': serialize_user(user)}), 201)

    @staticmethod
    def _create_student(user, profile_data):
        required_fields = ('name', 'roll_number', 'branch', 'cgpa', 'graduation_year')
        missing_fields = [field for field in required_fields if clean_text(profile_data.get(field)) in (None, '')]
        if missing_fields:
            raise ValueError(f"Missing fields: {', '.join(missing_fields)}.")
        try:
            cgpa = float(profile_data['cgpa'])
            graduation_year = int(profile_data['graduation_year'])
        except (TypeError, ValueError) as error:
            raise ValueError('CGPA and graduation year must be valid numbers.') from error
        if not 0 <= cgpa <= 10:
            raise ValueError('CGPA must be between 0 and 10.')
        roll_number = clean_text(profile_data['roll_number']).upper()
        existing_student = Student.query.filter(db.func.upper(Student.roll_number) == roll_number).first()
        if existing_student:
            raise ValueError(f'Roll number {roll_number} is already registered.')
        student = Student(user_id=user.id, name=clean_text(profile_data['name']), roll_number=roll_number, branch=clean_text(profile_data['branch']), cgpa=cgpa, graduation_year=graduation_year, phone=clean_text(profile_data.get('phone')), alternate_email=clean_text(profile_data.get('alternate_email')))
        db.session.add(student)
        return 'Student registered successfully.'

    @staticmethod
    def _create_company(user, profile_data):
        required_fields = ('company_name', 'hr_name', 'hr_email')
        missing_fields = [field for field in required_fields if clean_text(profile_data.get(field)) in (None, '')]
        if missing_fields:
            raise ValueError(f"Missing fields: {', '.join(missing_fields)}.")
        hr_email = clean_text(profile_data['hr_email']).lower()
        if not validate_email(hr_email):
            raise ValueError('Enter a valid HR email address.')
        company = Company(user_id=user.id, company_name=clean_text(profile_data['company_name']), company_description=clean_text(profile_data.get('company_description') or profile_data.get('description')), hr_name=clean_text(profile_data['hr_name']), hr_email=hr_email, hr_phone=clean_text(profile_data.get('hr_phone')), website=clean_text(profile_data.get('website')), industry=clean_text(profile_data.get('industry')), location=clean_text(profile_data.get('location')), approval_status='pending')
        db.session.add(company)
        return 'Company registered successfully. Your profile is pending admin approval.'

class LoginAPI(Resource):
    """Authenticate a user and return a Flask-Security token."""

    def post(self):
        data = request.get_json(silent=True) or {}
        email = clean_text(data.get('email', '')).lower()
        password = data.get('password', '')
        if not email or not password:
            return make_response(jsonify({'message': 'Email and password are required.'}), 400)
        user = user_datastore.find_user(email=email)
        if not user or not utils.verify_password(password, user.password):
            return make_response(jsonify({'message': 'Invalid email or password.'}), 401)
        if not user.active:
            return make_response(jsonify({'message': 'This account is deactivated. Contact the placement cell.'}), 403)
        if user.is_company and user.company_profile and user.company_profile.is_blacklisted:
            return make_response(jsonify({'message': 'This company account has been blacklisted.'}), 403)
        if user.is_student and user.student_profile and user.student_profile.is_blacklisted:
            return make_response(jsonify({'message': 'This student account has been blacklisted.'}), 403)
        login_user(user)
        previous_login_at = user.current_login_at
        previous_login_ip = user.current_login_ip
        now = datetime.utcnow()
        user.last_login_at = previous_login_at
        user.last_login_ip = previous_login_ip
        user.current_login_at = now
        user.current_login_ip = request.remote_addr
        user.login_count = (user.login_count or 0) + 1
        db.session.commit()
        return make_response(jsonify({'message': 'Login successful.', 'auth_token': user.get_auth_token(), 'user': serialize_user(user)}), 200)

class LogoutAPI(Resource):
    """End the current authenticated session."""

    @auth_token_required
    def post(self):
        logout_user()
        return make_response(jsonify({'message': 'Logout successful.'}), 200)

class ProfileAPI(Resource):
    """Return the current authenticated user's profile."""

    @auth_token_required
    def get(self):
        user_data = serialize_user(current_user)
        user_data.update({'active': current_user.active, 'last_login': current_user.last_login_at.isoformat() if current_user.last_login_at else None, 'current_login': current_user.current_login_at.isoformat() if current_user.current_login_at else None, 'login_count': current_user.login_count or 0})
        return make_response(jsonify({'user': user_data}), 200)

class ChangePasswordAPI(Resource):
    """Change the password of the authenticated user."""

    @auth_token_required
    def post(self):
        data = request.get_json(silent=True) or {}
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        if not current_password or not new_password or (not confirm_password):
            return make_response(jsonify({'message': 'All fields are required.'}), 400)
        if new_password != confirm_password:
            return make_response(jsonify({'message': 'New passwords do not match.'}), 400)
        if not utils.verify_password(current_password, current_user.password):
            return make_response(jsonify({'message': 'Current password is incorrect.'}), 401)
        if utils.verify_password(new_password, current_user.password):
            return make_response(jsonify({'message': 'New password must be different from the current password.'}), 400)
        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            return make_response(jsonify({'message': password_error}), 400)
        current_user.password = utils.hash_password(new_password)
        db.session.commit()
        return make_response(jsonify({'message': 'Password changed successfully.'}), 200)
