import csv
import os
from calendar import monthrange
from datetime import datetime, timedelta

from flask import current_app
from sqlalchemy import func

from celery_app import celery
from controllers.database import db
from controllers.models import (
    Application,
    Company,
    PlacementDrive,
    Role,
    Student,
    User,
)
from mail import send_email


def get_admin_emails():
    """Return email addresses for all active admin users."""

    admin_role = Role.query.filter_by(name=Role.ADMIN).first()

    if not admin_role:
        return []

    admins = (
        User.query
        .filter(
            User.active.is_(True),
            User.roles.contains(admin_role),
        )
        .all()
    )

    return [
        admin.email
        for admin in admins
        if admin.email
    ]


def student_is_eligible(student, drive):
    if drive.min_cgpa is not None and student.cgpa < drive.min_cgpa:
        return False

    if drive.allowed_branches:
        branch_aliases = {
            "cse": "computer science",
            "cs": "computer science",
            "computer science": "computer science",
            "it": "information technology",
            "information technology": "information technology",
            "ece": "electronics and communication",
            "electronics and communication": "electronics and communication",
            "ee": "electrical engineering",
            "electrical engineering": "electrical engineering",
            "me": "mechanical engineering",
            "mechanical engineering": "mechanical engineering",
            "ce": "civil engineering",
            "civil engineering": "civil engineering",
        }

        def normalize_branch(branch):
            branch = branch.strip().lower()
            return branch_aliases.get(branch, branch)

        student_branch = normalize_branch(student.branch)

        allowed_branches = [
            normalize_branch(branch)
            for branch in drive.allowed_branches.split(",")
            if branch.strip()
        ]

        if student_branch not in allowed_branches:
            return False

    return True


def get_previous_month_range(reference_date=None):
    """Return the first and final datetime of the previous calendar month."""

    reference_date = reference_date or datetime.utcnow()

    current_month_start = reference_date.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    previous_month_end = current_month_start - timedelta(microseconds=1)
    previous_month_start = previous_month_end.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    return previous_month_start, previous_month_end


@celery.task(name="tasks.send_daily_deadline_reminders")
def send_daily_deadline_reminders():
    """Email eligible students about drives closing within three days."""

    now = datetime.utcnow()
    reminder_limit = now + timedelta(days=3)

    upcoming_drives = (
        PlacementDrive.query
        .filter(
            PlacementDrive.status == "approved",
            PlacementDrive.application_deadline >= now,
            PlacementDrive.application_deadline <= reminder_limit,
        )
        .order_by(PlacementDrive.application_deadline.asc())
        .all()
    )

    if not upcoming_drives:
        return {
            "status": "success",
            "message": "No upcoming deadlines found.",
            "emails_sent": 0,
        }

    students = (
        Student.query
        .join(User, Student.user_id == User.id)
        .filter(
            Student.is_blacklisted.is_(False),
            User.active.is_(True),
        )
        .all()
    )

    emails_sent = 0

    for student in students:
        applied_drive_ids = {
            drive_id
            for (drive_id,) in (
                db.session.query(Application.drive_id)
                .filter_by(student_id=student.id)
                .all()
            )
        }

        relevant_drives = [
            drive
            for drive in upcoming_drives
            if drive.id not in applied_drive_ids
            and student_is_eligible(student, drive)
        ]

        if not relevant_drives or not student.user.email:
            continue

        drive_rows = "".join(
            (
                "<li>"
                f"<strong>{drive.drive_name}</strong> - "
                f"{drive.company.company_name if drive.company else 'Company'}"
                f"<br>Role: {drive.job_title}"
                f"<br>Deadline: "
                f"{drive.application_deadline.strftime('%d %B %Y, %I:%M %p')}"
                "</li>"
            )
            for drive in relevant_drives
        )

        html_body = f"""
        <h2>Upcoming placement deadlines</h2>

        <p>Hello {student.name},</p>

        <p>
            The following placement drives match your profile and
            have an upcoming application deadline:
        </p>

        <ul>
            {drive_rows}
        </ul>

        <p>
            Sign in to the Placement Portal to review the drive
            and submit your application before the deadline.
        </p>

        <p>Placement Cell</p>
        """

        success, _ = send_email(
            "Upcoming placement application deadlines",
            student.user.email,
            html_body,
        )

        if success:
            emails_sent += 1

    return {
        "status": "success",
        "message": f"Deadline reminders sent to {emails_sent} students.",
        "emails_sent": emails_sent,
        "drives_checked": len(upcoming_drives),
    }


@celery.task(name="tasks.send_new_drive_notification")
def send_new_drive_notification(drive_id):
    """Notify eligible students when an approved drive becomes available."""

    drive = db.session.get(PlacementDrive, drive_id)

    if not drive or drive.status != "approved":
        return {
            "status": "skipped",
            "message": "Drive is unavailable or not approved.",
        }

    students = (
        Student.query
        .join(User, Student.user_id == User.id)
        .filter(
            Student.is_blacklisted.is_(False),
            User.active.is_(True),
        )
        .all()
    )

    emails_sent = 0
    company_name = (
        drive.company.company_name
        if drive.company
        else "Company"
    )

    for student in students:
        if not student.user.email or not student_is_eligible(student, drive):
            continue

        existing_application = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id,
        ).first()

        if existing_application:
            continue

        html_body = f"""
        <h2>New placement drive available</h2>
        <p>Hello {student.name},</p>
        <p>
            <strong>{drive.drive_name}</strong> by
            <strong>{company_name}</strong> is now open for applications.
        </p>
        <p><strong>Role:</strong> {drive.job_title}</p>
        <p>
            <strong>Minimum CGPA:</strong>
            {drive.min_cgpa if drive.min_cgpa is not None else 'Not specified'}
        </p>
        <p>
            <strong>Allowed branches:</strong>
            {drive.allowed_branches or 'All branches'}
        </p>
        <p>
            <strong>Application deadline:</strong>
            {drive.application_deadline.strftime('%d %B %Y, %I:%M %p')} UTC
        </p>
        <p>Sign in to the Placement Portal to view the complete drive.</p>
        <p>Placement Cell</p>
        """

        success, _ = send_email(
            f"New placement drive: {drive.drive_name}",
            student.user.email,
            html_body,
        )

        if success:
            emails_sent += 1

    return {
        "status": "success",
        "message": f"New drive notification sent to {emails_sent} students.",
        "emails_sent": emails_sent,
        "drive_id": drive.id,
    }


def build_monthly_report(start_dt, end_dt):
    """Build the monthly placement report and return its HTML and metrics."""

    drives_count = (
        PlacementDrive.query
        .filter(
            PlacementDrive.created_at >= start_dt,
            PlacementDrive.created_at <= end_dt,
            PlacementDrive.status.in_(["approved", "closed"]),
        )
        .count()
    )

    applications_count = (
        Application.query
        .filter(
            Application.applied_at >= start_dt,
            Application.applied_at <= end_dt,
        )
        .count()
    )

    selections_count = (
        Application.query
        .filter(
            Application.selected_at.isnot(None),
            Application.selected_at >= start_dt,
            Application.selected_at <= end_dt,
        )
        .count()
    )

    top_companies = (
        db.session.query(
            Company.company_name,
            func.count(Application.id).label("selection_count"),
        )
        .join(
            PlacementDrive,
            Company.id == PlacementDrive.company_id,
        )
        .join(
            Application,
            PlacementDrive.id == Application.drive_id,
        )
        .filter(
            Application.selected_at.isnot(None),
            Application.selected_at >= start_dt,
            Application.selected_at <= end_dt,
        )
        .group_by(
            Company.id,
            Company.company_name,
        )
        .order_by(func.count(Application.id).desc())
        .limit(5)
        .all()
    )

    period_label = start_dt.strftime("%B %Y")

    company_rows = "".join(
        (
            "<tr>"
            f"<td>{company_name}</td>"
            f"<td>{selection_count}</td>"
            "</tr>"
        )
        for company_name, selection_count in top_companies
    )

    if not company_rows:
        company_rows = (
            '<tr><td colspan="2">No selections recorded.</td></tr>'
        )

    html_report = f"""
    <!DOCTYPE html>
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2937;">
        <h2>Monthly Placement Activity Report — {period_label}</h2>
        <p>
          Reporting period: {start_dt.strftime('%d %B %Y')} to
          {end_dt.strftime('%d %B %Y')}
        </p>

        <table
          cellpadding="8"
          cellspacing="0"
          border="1"
          style="border-collapse: collapse; width: 100%; max-width: 620px;"
        >
          <tr>
            <th align="left">Metric</th>
            <th align="left">Count</th>
          </tr>
          <tr>
            <td>Placement drives conducted</td>
            <td>{drives_count}</td>
          </tr>
          <tr>
            <td>Applications submitted</td>
            <td>{applications_count}</td>
          </tr>
          <tr>
            <td>Students selected</td>
            <td>{selections_count}</td>
          </tr>
        </table>

        <h3>Top companies by selections</h3>
        <table
          cellpadding="8"
          cellspacing="0"
          border="1"
          style="border-collapse: collapse; width: 100%; max-width: 620px;"
        >
          <tr>
            <th align="left">Company</th>
            <th align="left">Selections</th>
          </tr>
          {company_rows}
        </table>

        <p>
          Generated by the Placement Portal on
          {datetime.utcnow().strftime('%d %B %Y, %I:%M %p')} UTC.
        </p>
      </body>
    </html>
    """

    metrics = {
        "month": period_label,
        "period": {
            "from": start_dt.date().isoformat(),
            "to": end_dt.date().isoformat(),
        },
        "drives_conducted": drives_count,
        "students_applied": applications_count,
        "students_selected": selections_count,
        "top_companies": [
            {
                "company": company_name,
                "selections": int(selection_count),
            }
            for company_name, selection_count in top_companies
        ],
    }

    return html_report, metrics


@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report():
    """Generate and email the previous calendar month's activity report."""

    start_dt, end_dt = get_previous_month_range()
    html_report, metrics = build_monthly_report(start_dt, end_dt)

    admin_emails = get_admin_emails()
    emails_sent = 0

    for email in admin_emails:
        success, _ = send_email(
            f"Monthly Placement Report — {metrics['month']}",
            email,
            html_report,
        )

        if success:
            emails_sent += 1

    return {
        "status": "success",
        "message": f"Monthly report sent to {emails_sent} admins.",
        "emails_sent": emails_sent,
        "data": metrics,
    }


@celery.task(name="tasks.generate_scheduled_monthly_report")
def generate_scheduled_monthly_report():
    """Scheduled entry point used by Celery Beat on the first of each month."""

    return generate_monthly_report()


@celery.task(
    bind=True,
    name="tasks.export_student_applications",
    autoretry_for=(OSError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def export_student_applications(self, student_id):
    """Export a student's application history to a CSV file."""

    student = db.session.get(Student, student_id)

    if not student:
        return {
            "status": "failed",
            "message": f"Student {student_id} was not found.",
        }

    applications = (
        Application.query
        .filter_by(student_id=student.id)
        .order_by(Application.applied_at.desc())
        .all()
    )

    export_folder = current_app.config["EXPORT_FOLDER"]
    os.makedirs(export_folder, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = (
        f"student_{student.id}_applications_{timestamp}.csv"
    )
    file_path = os.path.join(export_folder, filename)

    fieldnames = [
        "Student ID",
        "Company Name",
        "Drive Title",
        "Application Status",
        "Application Date",
        "Interview Date",
        "Last Updated",
    ]

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for application in applications:
            drive = application.drive
            company = drive.company if drive else None

            writer.writerow(
                {
                    "Student ID": student.roll_number,
                    "Company Name": (
                        company.company_name
                        if company
                        else ""
                    ),
                    "Drive Title": (
                        drive.drive_name
                        if drive
                        else ""
                    ),
                    "Application Status": application.status,
                    "Application Date": (
                        application.applied_at.isoformat()
                        if application.applied_at
                        else ""
                    ),
                    "Interview Date": (
                        application.interview_date.isoformat()
                        if application.interview_date
                        else ""
                    ),
                    "Last Updated": (
                        application.updated_at.isoformat()
                        if application.updated_at
                        else ""
                    ),
                }
            )

    return {
        "status": "success",
        "message": "Application history exported successfully.",
        "student_id": student.id,
        "application_count": len(applications),
        "filename": filename,
        "file_path": file_path,
    }
