# Cloud-Based Student Management System (Flask + Firebase)

This is a minimal starter you can deploy quickly. It uses:
- **Firebase Firestore** (Database-as-a-Service)
- **Flask** (Python web framework)
- Simple HTML/CSS templates (server-rendered)

## 1) Firebase Setup (once)

1. Go to Firebase Console → Create a Project.
2. In *Build → Firestore Database*, create a database (Start in test mode for local dev).
3. In *Project Settings → Service accounts → Python*, click **Generate new private key** and download the JSON.
4. Put the file at the project root as `firebase_key.json` (or set `GOOGLE_APPLICATION_CREDENTIALS` to the file path).

**Firestore structure** (created on the fly):
```
students (collection)
  └─ <student_id> (doc)
       name, email, std_class, section, dob, updated_at
       ├─ grades (subcollection)
       │    └─ autoId: subject, score, term, created_at
       └─ attendance (subcollection)
            └─ <YYYY-MM-DD>: date, status
```

## 2) Local Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Copy env template and edit
cp .env.example .env
# set ADMIN_USERNAME, ADMIN_PASSWORD, FLASK_SECRET_KEY, GOOGLE_APPLICATION_CREDENTIALS

# run
python app.py
# open http://localhost:5000
```

## 3) Demo Flow

- Go to **Admin Login** → use the credentials from your `.env`.
- In the **Dashboard**:
  - Add/Update Student (ID, name, etc.).
  - Add a Grade.
  - Mark Attendance.
- Go to **Student Portal**:
  - Enter Student ID + DOB to view grades/attendance.

## 4) Deploy (Render, simple)

1. Push this folder to a Git repo.
2. Create a new **Web Service** on Render (start command: `gunicorn app:app`).
3. Add environment variables:
   - `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `FLASK_SECRET_KEY`
4. Add the `firebase_key.json` via Render *Secret Files* (and set `GOOGLE_APPLICATION_CREDENTIALS=firebase_key.json`).

Alternatively, containerize and deploy to Google Cloud Run.

## 5) Security Notes

This demo keeps all writes server-side. If you later build a client that talks directly to Firestore, set Firestore Rules to deny client writes or constrain them tightly.

## 6) Next Steps

- Proper admin auth (Firebase Auth / Flask-Login + hashed passwords).
- CSV import/export.
- Pagination and search.
- Per-student accounts.
- Report downloads (CSV/PDF).
