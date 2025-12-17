import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY","dev-secret-key")

# Firebase / Firestore
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS","firebase_key.json")

if not firebase_admin._apps:
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # If using emulator, allow init without file present
        firebase_admin.initialize_app()
db = firestore.client()

def is_admin():
    return session.get("admin") is True

@app.get('/')
def home():
    return render_template("home.html")

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username','')
        p = request.form.get('password','')
        if (u == os.environ.get('ADMIN_USERNAME','admin') 
            and p == os.environ.get('ADMIN_PASSWORD','changeme123')):
            session['admin'] = True
            flash('Logged in as admin','success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials','error')
    return render_template('admin_login.html')

@app.get('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out','success')
    return redirect(url_for('home'))

@app.get('/admin')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))
    students = db.collection('students').stream()
    today = date.today().isoformat()
    return render_template('admin_dashboard.html', students=students, today=today)

@app.post('/admin/add-student')
def add_student():
    if not is_admin():
        return redirect(url_for('admin_login'))
    data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'std_class': request.form.get('std_class'),
        'section': request.form.get('section'),
        'dob': request.form.get('dob'),
        'updated_at': datetime.utcnow()
    }
    sid = request.form.get('student_id')
    if not sid:
        flash('Student ID required','error')
        return redirect(url_for('admin_dashboard'))
    db.collection('students').document(sid).set(data, merge=True)
    flash(f'Student {sid} saved','success')
    return redirect(url_for('admin_dashboard'))

@app.post('/admin/add-grade')
def add_grade():
    if not is_admin():
        return redirect(url_for('admin_login'))
    sid = request.form.get('student_id')
    subject = request.form.get('subject')
    score = request.form.get('score')
    term = request.form.get('term')
    if not all([sid, subject, score]):
        flash('Student, subject, and score required','error')
        return redirect(url_for('admin_dashboard'))
    payload = {'subject':subject,'score':score,'term':term,'created_at':datetime.utcnow()}
    db.collection('students').document(sid).collection('grades').add(payload)
    flash('Grade added','success')
    return redirect(url_for('admin_dashboard'))

@app.post('/admin/mark-attendance')
def mark_attendance():
    if not is_admin():
        return redirect(url_for('admin_login'))
    sid = request.form.get('student_id')
    d = request.form.get('date') or date.today().isoformat()
    status = request.form.get('status','Present')
    if not sid:
        flash('Student required','error')
        return redirect(url_for('admin_dashboard'))
    db.collection('students').document(sid).collection('attendance').document(d).set({
        'date': d,
        'status': status
    })
    flash('Attendance marked','success')
    return redirect(url_for('admin_dashboard'))

@app.route('/student', methods=['GET','POST'])
def student_lookup():
    if request.method == 'POST':
        sid = request.form.get('student_id')
        dob = request.form.get('dob')
        doc = db.collection('students').document(sid).get()
        if not doc.exists:
            flash('Student not found','error')
            return redirect(url_for('student_lookup'))
        student = doc.to_dict()
        if student.get('dob') != dob:
            flash('DOB does not match our records','error')
            return redirect(url_for('student_lookup'))

        grades_ref = db.collection('students').document(sid).collection('grades').order_by('created_at', direction=firestore.Query.DESCENDING).limit(10)
        grades = [g.to_dict() for g in grades_ref.stream()]
        att_ref = db.collection('students').document(sid).collection('attendance').order_by('date', direction=firestore.Query.DESCENDING).limit(20)
        attendance = [a.to_dict() for a in att_ref.stream()]
        return render_template('student_view.html', student=student, sid=sid, grades=grades, attendance=attendance)
    return render_template('student_lookup.html')

@app.get('/healthz')
def healthz():
    return {'ok': True}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
