from datetime import datetime

from flask_security import RoleMixin, UserMixin

from controllers.database import db


class UserRoles(db.Model):
    """Association table connecting users with their roles."""

    __tablename__ = "user_roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id"),
        nullable=False,
    )


class Role(db.Model, RoleMixin):
    """Application roles used for role-based access control."""

    __tablename__ = "role"

    ADMIN = "admin"
    COMPANY = "company"
    STUDENT = "student"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
    )
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Role {self.name}>"


class User(db.Model, UserMixin):
    """Common authentication model for every application user."""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
    )
    password = db.Column(
        db.String(255),
        nullable=False,
    )
    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    # Required by Flask-Security-Too.
    fs_uniquifier = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
    )
    fs_token_uniquifier = db.Column(
        db.String(255),
        unique=True,
        nullable=True,
    )

    # Flask-Security trackable fields.
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(
        db.Integer,
        default=0,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    roles = db.relationship(
        "Role",
        secondary="user_roles",
        backref=db.backref(
            "users",
            lazy="dynamic",
        ),
    )

    student_profile = db.relationship(
        "Student",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="Student.user_id",
    )

    company_profile = db.relationship(
        "Company",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="Company.user_id",
    )

    @property
    def is_admin(self):
        return any(
            role.name == Role.ADMIN
            for role in self.roles
        )

    @property
    def is_company(self):
        return any(
            role.name == Role.COMPANY
            for role in self.roles
        )

    @property
    def is_student(self):
        return any(
            role.name == Role.STUDENT
            for role in self.roles
        )

    def get_role_name(self):
        """Return the primary role assigned to the user."""

        if not self.roles:
            return None

        return self.roles[0].name

    def get_profile(self):
        """Return the profile associated with the user's role."""

        if self.is_student:
            return self.student_profile

        if self.is_company:
            return self.company_profile

        return None

    def __repr__(self):
        return f"<User {self.email}>"


class Student(db.Model):
    """Student profile and placement-related information."""

    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False,
    )

    name = db.Column(
        db.String(255),
        nullable=False,
    )
    roll_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
    )
    branch = db.Column(
        db.String(100),
        nullable=False,
    )
    cgpa = db.Column(
        db.Float,
        nullable=False,
    )
    graduation_year = db.Column(
        db.Integer,
        nullable=False,
    )

    phone = db.Column(db.String(20))
    alternate_email = db.Column(db.String(255))

    resume_path = db.Column(db.String(255))
    resume_filename = db.Column(db.String(255))
    resume_uploaded_at = db.Column(db.DateTime)

    is_blacklisted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )
    blacklist_reason = db.Column(db.String(500))
    blacklisted_at = db.Column(db.DateTime)
    blacklisted_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    applications = db.relationship(
        "Application",
        backref="student",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        """Return student data in an API-friendly format."""

        return {
            "id": self.id,
            "name": self.name,
            "roll_number": self.roll_number,
            "branch": self.branch,
            "cgpa": self.cgpa,
            "graduation_year": self.graduation_year,
            "phone": self.phone,
            "alternate_email": self.alternate_email,
            "email": (
                self.user.email
                if self.user
                else None
            ),
            "has_resume": bool(self.resume_path),
            "resume_filename": self.resume_filename,
            "resume_uploaded_at": (
                self.resume_uploaded_at.isoformat()
                if self.resume_uploaded_at
                else None
            ),
            "is_blacklisted": self.is_blacklisted,
            "blacklist_reason": self.blacklist_reason,
            "blacklisted_at": (
                self.blacklisted_at.isoformat()
                if self.blacklisted_at
                else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return (
            f"<Student {self.roll_number}: "
            f"{self.name}>"
        )


class Company(db.Model):
    """Company profile and institute approval information."""

    __tablename__ = "company"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False,
    )

    company_name = db.Column(
        db.String(255),
        nullable=False,
    )
    company_description = db.Column(db.Text)

    hr_name = db.Column(
        db.String(255),
        nullable=False,
    )
    hr_email = db.Column(
        db.String(255),
        nullable=False,
    )
    hr_phone = db.Column(db.String(20))

    website = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(255))
    logo_path = db.Column(db.String(255))

    approval_status = db.Column(
        db.String(50),
        default="pending",
        nullable=False,
    )
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
    )
    rejection_reason = db.Column(db.String(500))

    is_blacklisted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )
    blacklist_reason = db.Column(db.String(500))
    blacklisted_at = db.Column(db.DateTime)
    blacklisted_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    drives = db.relationship(
        "PlacementDrive",
        backref="company",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        """Return company data in an API-friendly format."""

        return {
            "id": self.id,
            "company_name": self.company_name,
            "company_description": self.company_description,
            "hr_name": self.hr_name,
            "hr_email": self.hr_email,
            "hr_phone": self.hr_phone,
            "website": self.website,
            "industry": self.industry,
            "location": self.location,
            "logo_path": self.logo_path,
            "approval_status": self.approval_status,
            "approved_at": (
                self.approved_at.isoformat()
                if self.approved_at
                else None
            ),
            "rejection_reason": self.rejection_reason,
            "is_blacklisted": self.is_blacklisted,
            "blacklist_reason": self.blacklist_reason,
            "blacklisted_at": (
                self.blacklisted_at.isoformat()
                if self.blacklisted_at
                else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return f"<Company {self.company_name}>"


class PlacementDrive(db.Model):
    """Recruitment drive created by an approved company."""

    __tablename__ = "placement_drive"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False,
    )

    drive_name = db.Column(
        db.String(255),
        nullable=False,
    )
    job_title = db.Column(
        db.String(255),
        nullable=False,
    )
    job_description = db.Column(db.Text)

    eligibility_criteria = db.Column(db.Text)
    min_cgpa = db.Column(db.Float)
    allowed_branches = db.Column(db.String(500))

    application_deadline = db.Column(
        db.DateTime,
        nullable=False,
    )
    drive_date = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    status = db.Column(
        db.String(50),
        default="pending",
        nullable=False,
    )
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
    )

    applications = db.relationship(
        "Application",
        backref="drive",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        """Return placement drive data for API responses."""

        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": (
                self.company.company_name
                if self.company
                else None
            ),
            "drive_name": self.drive_name,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "eligibility_criteria": self.eligibility_criteria,
            "min_cgpa": self.min_cgpa,
            "allowed_branches": self.allowed_branches,
            "application_deadline": (
                self.application_deadline.isoformat()
                if self.application_deadline
                else None
            ),
            "drive_date": (
                self.drive_date.isoformat()
                if self.drive_date
                else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "status": self.status,
            "approved_at": (
                self.approved_at.isoformat()
                if self.approved_at
                else None
            ),
            "application_count": self.applications.count(),
        }

    def __repr__(self):
        return f"<PlacementDrive {self.drive_name}>"


class Application(db.Model):
    """Student application submitted for a placement drive."""

    __tablename__ = "application"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False,
    )
    drive_id = db.Column(
        db.Integer,
        db.ForeignKey("placement_drive.id"),
        nullable=False,
    )

    status = db.Column(
        db.String(50),
        default="applied",
        nullable=False,
    )
    applied_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    interview_date = db.Column(db.DateTime)
    interview_notes = db.Column(db.Text)

    shortlisted_at = db.Column(db.DateTime)
    selected_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.String(500))

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "drive_id",
            name="unique_application",
        ),
    )

    def to_dict(self):
        """Return complete application information."""

        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": (
                self.student.name
                if self.student
                else None
            ),
            "student_roll_number": (
                self.student.roll_number
                if self.student
                else None
            ),
            "drive_id": self.drive_id,
            "drive_name": (
                self.drive.drive_name
                if self.drive
                else None
            ),
            "job_title": (
                self.drive.job_title
                if self.drive
                else None
            ),
            "company_name": (
                self.drive.company.company_name
                if self.drive and self.drive.company
                else None
            ),
            "status": self.status,
            "applied_at": (
                self.applied_at.isoformat()
                if self.applied_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
            "interview_date": (
                self.interview_date.isoformat()
                if self.interview_date
                else None
            ),
            "interview_notes": self.interview_notes,
            "shortlisted_at": (
                self.shortlisted_at.isoformat()
                if self.shortlisted_at
                else None
            ),
            "selected_at": (
                self.selected_at.isoformat()
                if self.selected_at
                else None
            ),
            "rejected_at": (
                self.rejected_at.isoformat()
                if self.rejected_at
                else None
            ),
            "rejection_reason": self.rejection_reason,
        }

    def __repr__(self):
        return f"<Application {self.id}>"