# Placement Portal Application - V2

Placement Portal is a simple campus recruitment management system for institutes, companies and students.

It was built as a role-based web application using Flask, Vue.js, SQLite, Redis and Celery.

## What the application does

### Admin

- View students, companies, placement drives and applications
- Approve or reject company registrations
- Approve, reject and close placement drives
- Search students and companies
- Blacklist or reactivate student and company accounts
- View placement statistics
- View student resumes
- Trigger the monthly placement activity report

### Company

- Register and maintain a company profile
- Create placement drives after admin approval
- View applications received for company drives
- View applicant resumes
- Shortlist or reject students
- Schedule interviews
- Mark shortlisted students as selected
- Update or remove placement drives

### Student

- Register and log in
- Update profile details
- Upload and replace a PDF resume
- Browse approved placement drives
- Search and filter drives
- Apply only when eligible
- Track application status
- View complete placement history
- Export application history as CSV using a Celery background job

The application also prevents a student from applying to the same drive more than once.

## Tech stack

**Backend:** Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Security-Too, SQLite, Redis, Celery, Flask-Caching and Flask-Mail.

**Frontend:** Vue 3, Vue Router, Pinia, Axios, Bootstrap 5, Bootstrap Icons and Vite.

## Project structure

```text
Placement_Portal_V2/
├── backend/
│   ├── controllers/
│   │   ├── authentication_apis.py
│   │   ├── config.py
│   │   ├── crud_apis.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── user_datastore.py
│   ├── app.py
│   ├── celery_app.py
│   ├── celery_worker.py
│   ├── extension.py
│   ├── mail.py
│   ├── tasks.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── router/
│   │   ├── services/
│   │   ├── stores/
│   │   └── views/
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Requirements

Install the following before running the project:

- Python 3.10 or newer
- Node.js 20.19+ or 22.12+
- Redis

The commands below are written for Windows PowerShell.

## 1. Configure the backend

Open a terminal in the project folder:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create your local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Open `backend/.env` and add your local settings. If email is required, enter a valid SMTP account and app password.

Do not commit the `.env` file to GitHub.

## 2. Start Redis

Redis must be available at `127.0.0.1:6379`.

If Redis is installed in WSL:

```powershell
wsl redis-server
```

If port 6379 is already in use, Redis is probably already running. Check it inside WSL with:

```bash
redis-cli ping
```

The expected response is:

```text
PONG
```

## 3. Start the Flask backend

From the `backend` folder with the virtual environment active:

```powershell
python app.py
```

The backend runs at `http://127.0.0.1:5000`.

The SQLite database, application tables, roles and admin account are created programmatically when the backend starts.

## 4. Start the Celery worker

Open a new PowerShell terminal:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m celery -A celery_worker.celery worker --pool=solo --loglevel=info
```

The `solo` pool is used for Windows compatibility.

## 5. Start Celery Beat

Open another PowerShell terminal:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m celery -A celery_worker.celery beat --loglevel=info
```

Celery Beat runs the scheduled reminder and monthly report jobs.

## 6. Start the Vue frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite, normally `http://127.0.0.1:5173`.

## Recommended run order

```text
1. Redis
2. Flask backend
3. Celery worker
4. Celery Beat
5. Vue frontend
```

## Default admin account

The admin account is created automatically. There is no admin registration page.

```text
Email: admin@placement.edu
Password: Admin@123
```

The values can be changed using `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `backend/.env` before creating a fresh database.

## Background jobs

The project contains three main background workflows:

- **Daily deadline reminders:** checks for approved drives closing soon and emails eligible students who have not applied.
- **Monthly activity report:** creates the previous month's placement report and emails it to the admin.
- **Application CSV export:** the student starts an export, Celery creates the CSV, the frontend waits for completion and downloads the generated file.

## Caching

Redis-backed caching is used for the admin dashboard. Cached dashboard data expires automatically and is cleared after important administrative updates.