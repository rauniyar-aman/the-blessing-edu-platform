# The Blessing Edu – Smart Global Admission Platform

## Repo Structure
```
backend/   # Django + DRF API
frontend/  # React (Vite) + React Router + React Query
```

## Backend Setup (Django + DRF)
1. Create a virtual environment and install dependencies:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
3. Run migrations and seed data:
   ```bash
   python manage.py migrate
   python manage.py loaddata core/fixtures/seed.json
   ```
4. Create a super admin:
   ```bash
   python manage.py createsuperuser
   ```
5. Start the API server:
   ```bash
   python manage.py runserver
   ```

### Key Backend Notes
- JWT auth endpoints:
  - `POST /api/auth/token/`
  - `POST /api/auth/token/refresh/`
- Email service uses console output in development.
- File storage uses local filesystem in development. Set `USE_S3=true` and AWS variables for S3-compatible storage.

## Frontend Setup (React + Vite)
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
3. Run the dev server:
   ```bash
   npm run dev
   ```

## MVP Scope
- Role-based portals for admin/staff, agency, and direct students.
- Agency registration workflow with admin approval.
- Country-specific pipelines (UK/USA) and stage change notifications.
- Document library with versioning and attachments.
- Tasks and auto-assignment rules.
- Commission structure and commission earned tracking.
- Course finder and eligibility UI scaffolds.

## Environment Variables
### Backend
See `backend/.env.example`.

### Frontend
See `frontend/.env.example`.
