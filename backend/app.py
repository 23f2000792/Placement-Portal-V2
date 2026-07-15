import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_security import Security
from flask_security import utils

from celery_app import celery
from controllers.config import Config
from controllers.database import db
from controllers.user_datastore import user_datastore
from extension import init_extension
from mail import init_mail


def configure_celery(app):
    celery.conf.update(app.config)

    class FlaskContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskContextTask


def initialize_database(app):
    with app.app_context():
        db.create_all()

        admin_role = user_datastore.find_or_create_role(
            name="admin",
            description="Institute Placement Cell Administrator",
        )

        user_datastore.find_or_create_role(
            name="company",
            description="Registered Company",
        )

        user_datastore.find_or_create_role(
            name="student",
            description="Student Seeking Placement",
        )

        admin_email = app.config.get(
            "ADMIN_EMAIL",
            "admin@placement.edu",
        )
        admin_password = app.config.get(
            "ADMIN_PASSWORD",
            "Admin@123",
        )

        if not user_datastore.find_user(email=admin_email):
            user_datastore.create_user(
                email=admin_email,
                password=utils.hash_password(admin_password),
                roles=[admin_role],
            )

        db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Security(app, user_datastore)

    init_mail(app)
    init_extension(app)
    configure_celery(app)

    os.makedirs(
        app.config["EXPORT_FOLDER"],
        exist_ok=True,
    )

    os.makedirs(
        app.config["RESUME_FOLDER"],
        exist_ok=True,
    )

    CORS(
        app,
        origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
    )

    api = Api(app, prefix="/api")

    initialize_database(app)
    register_routes(app, api)
    register_error_handlers(app)

    return app


def register_routes(app, api):
    from controllers.authentication_apis import (
        ChangePasswordAPI,
        CheckEmailAPI,
        LoginAPI,
        LogoutAPI,
        ProfileAPI,
        RegisterAPI,
    )

    from controllers.crud_apis import (
        AdminApplicationsAPI,
        AdminCompanyActivateAPI,
        AdminCompanyApproveAPI,
        AdminCompanyBlacklistAPI,
        AdminCompanyDetailAPI,
        AdminCompanyListAPI,
        AdminCompanyRejectAPI,
        AdminDashboardAPI,
        AdminDriveApproveAPI,
        AdminDriveCloseAPI,
        AdminDriveDetailAPI,
        AdminDriveListAPI,
        AdminDriveRejectAPI,
        AdminGenerateMonthlyReportAPI,
        AdminSearchAPI,
        AdminStudentActivateAPI,
        AdminStudentBlacklistAPI,
        AdminStudentDetailAPI,
        AdminStudentListAPI,
        AdminTaskStatusAPI,
        AdminSendDeadlineRemindersAPI,
        CompanyApplicationDetailAPI,
        CompanyApplicationListAPI,
        CompanyApplicationRejectAPI,
        CompanyApplicationsAPI,
        CompanyApplicationSelectAPI,
        CompanyApplicationShortlistAPI,
        CompanyDashboardAPI,
        CompanyDriveCreateAPI,
        CompanyDriveDetailAPI,
        CompanyDriveListAPI,
        CompanyInterviewScheduleAPI,
        CompanyProfileAPI,
        StudentApplicationDetailAPI,
        StudentApplicationListAPI,
        StudentApplyAPI,
        StudentDashboardAPI,
        StudentDeleteApplicationAPI,
        StudentDriveDetailAPI,
        StudentDriveListAPI,
        StudentExportApplicationsAPI,
        StudentHistoryAPI,
        StudentProfileAPI,
        StudentExportDownloadAPI,
        StudentExportStatusAPI,
        StudentResumeAPI,
        AdminStudentResumeAPI,
        CompanyStudentResumeAPI,
    )

    api.add_resource(LoginAPI, "/login")
    api.add_resource(LogoutAPI, "/logout")
    api.add_resource(RegisterAPI, "/register")
    api.add_resource(CheckEmailAPI, "/check-email")
    api.add_resource(ProfileAPI, "/profile")
    api.add_resource(ChangePasswordAPI, "/change-password")

    api.add_resource(
        AdminDashboardAPI,
        "/admin/dashboard",
    )
    api.add_resource(
        AdminApplicationsAPI,
        "/admin/applications",
    )
    api.add_resource(
        AdminCompanyListAPI,
        "/admin/companies",
    )
    api.add_resource(
        AdminCompanyDetailAPI,
        "/admin/companies/<int:company_id>",
    )
    api.add_resource(
        AdminCompanyApproveAPI,
        "/admin/companies/<int:company_id>/approve",
    )
    api.add_resource(
        AdminCompanyRejectAPI,
        "/admin/companies/<int:company_id>/reject",
    )
    api.add_resource(
        AdminCompanyBlacklistAPI,
        "/admin/companies/<int:company_id>/blacklist",
    )
    api.add_resource(
        AdminCompanyActivateAPI,
        "/admin/companies/<int:company_id>/activate",
    )

    api.add_resource(
        AdminDriveListAPI,
        "/admin/drives",
    )
    api.add_resource(
        AdminDriveDetailAPI,
        "/admin/drives/<int:drive_id>",
    )
    api.add_resource(
        AdminDriveApproveAPI,
        "/admin/drives/<int:drive_id>/approve",
    )
    api.add_resource(
        AdminDriveRejectAPI,
        "/admin/drives/<int:drive_id>/reject",
    )
    api.add_resource(
        AdminDriveCloseAPI,
        "/admin/drives/<int:drive_id>/close",
    )

    api.add_resource(
        AdminStudentListAPI,
        "/admin/students",
    )
    api.add_resource(
        AdminStudentDetailAPI,
        "/admin/students/<int:student_id>",
    )
    api.add_resource(
        AdminStudentBlacklistAPI,
        "/admin/students/<int:student_id>/blacklist",
    )
    api.add_resource(
        AdminStudentActivateAPI,
        "/admin/students/<int:student_id>/activate",
    )

    api.add_resource(
        AdminSearchAPI,
        "/admin/search",
    )
    api.add_resource(
        AdminGenerateMonthlyReportAPI,
        "/admin/reports/monthly",
    )
    api.add_resource(
        AdminTaskStatusAPI,
        "/admin/tasks/<string:task_id>",
    )
    api.add_resource(
        AdminSendDeadlineRemindersAPI,
        "/admin/reminders/send",
    )

    api.add_resource(
        StudentProfileAPI,
        "/student/profile",
    )
    api.add_resource(
        StudentDashboardAPI,
        "/student/dashboard",
    )
    api.add_resource(
        StudentDriveListAPI,
        "/student/drives",
    )
    api.add_resource(
        StudentDriveDetailAPI,
        "/student/drives/<int:drive_id>",
    )
    api.add_resource(
        StudentApplyAPI,
        "/student/drives/<int:drive_id>/apply",
    )
    api.add_resource(
        StudentApplicationListAPI,
        "/student/applications",
    )
    api.add_resource(
        StudentApplicationDetailAPI,
        "/student/applications/<int:application_id>",
    )
    api.add_resource(
        StudentDeleteApplicationAPI,
        "/student/applications/<int:application_id>",
    )
    api.add_resource(
        StudentHistoryAPI,
        "/student/history",
    )
    api.add_resource(
        StudentExportApplicationsAPI,
        "/student/export/applications",
    )

    api.add_resource(
        StudentExportStatusAPI,
        "/student/export/applications/<string:task_id>",
    )

    api.add_resource(
        StudentExportDownloadAPI,
        "/student/export/download/<string:filename>",
    )

    api.add_resource(
        StudentResumeAPI,
        "/student/resume",
    )

    api.add_resource(
        AdminStudentResumeAPI,
        "/admin/students/<int:student_id>/resume",
    )

    api.add_resource(
        CompanyStudentResumeAPI,
        "/company/students/<int:student_id>/resume",
    )

    api.add_resource(
        CompanyProfileAPI,
        "/company/profile",
    )
    api.add_resource(
        CompanyDashboardAPI,
        "/company/dashboard",
    )
    api.add_resource(
        CompanyDriveCreateAPI,
        "/company/drives",
    )
    api.add_resource(
        CompanyDriveListAPI,
        "/company/drives",
    )
    api.add_resource(
        CompanyDriveDetailAPI,
        "/company/drives/<int:drive_id>",
    )
    api.add_resource(
        CompanyApplicationListAPI,
        "/company/drives/<int:drive_id>/applications",
    )
    api.add_resource(
        CompanyApplicationsAPI,
        "/company/applications",
    )
    api.add_resource(
        CompanyApplicationDetailAPI,
        "/company/applications/<int:application_id>",
    )
    api.add_resource(
        CompanyApplicationShortlistAPI,
        "/company/applications/<int:application_id>/shortlist",
    )
    api.add_resource(
        CompanyApplicationSelectAPI,
        "/company/applications/<int:application_id>/select",
    )
    api.add_resource(
        CompanyApplicationRejectAPI,
        "/company/applications/<int:application_id>/reject",
    )
    api.add_resource(
        CompanyInterviewScheduleAPI,
        "/company/applications/<int:application_id>/schedule-interview",
    )

    @app.get("/")
    def index():
        return {
            "name": "Placement Portal API",
            "version": "2.0",
            "status": "running",
        }, 200

    @app.get("/health")
    def health():
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, 200


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_error):
        return {
            "success": False,
            "message": "Endpoint not found",
        }, 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()

        return {
            "success": False,
            "message": "Internal server error",
        }, 500


app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )