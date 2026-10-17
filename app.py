# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from db_connect import get_connection
from datetime import datetime, timedelta, date
import secrets
import math

app = Flask(__name__)
app.secret_key = "change_this_secret"  # change in production

# ----------------- Helpers -----------------
def haversine_distance_m(lat1, lon1, lat2, lon2):
    # returns distance in meters
    R = 6371000
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# debugging helper — optional, remove later
@app.route("/routes")
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.endpoint:30}  ->  {rule.rule}")
    return "<pre>" + "\n".join(sorted(routes)) + "</pre>"

# ---- Home / Login ----
@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        identifier = request.form.get("email_or_id", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_connection()
        if not conn:
            flash("Database connection failed", "danger")
            return redirect(url_for("login"))

        cursor = conn.cursor(dictionary=True)
        try:
            if role == "teacher":
                cursor.execute(
                    "SELECT * FROM teachers WHERE (id=%s OR email=%s) AND password=%s",
                    (identifier, identifier, password)
                )
                user = cursor.fetchone()
                if not user:
                    flash("Invalid teacher credentials", "danger")
                    return redirect(url_for("login"))
                if user.get('status') != 'Approved':
                    flash(f"Your account status: {user.get('status')}. Wait for admin approval.", "warning")
                    return redirect(url_for("login"))

                session['role'] = 'teacher'
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                return redirect(url_for("teacher_dashboard"))

            elif role == "student":
                cursor.execute(
                    "SELECT * FROM students WHERE roll_no=%s AND password=%s",
                    (identifier, password)
                )
                user = cursor.fetchone()
                if not user:
                    flash("Invalid student credentials", "danger")
                    return redirect(url_for("login"))

                session['role'] = 'student'
                session['user_id'] = user['roll_no']
                session['user_name'] = user['name']
                return redirect(url_for("student_dashboard"))

            elif role == "admin":
                # simple hardcoded admin (or change to DB-based)
                if identifier == "devanshu" and password == "devanshu123":
                    session['role'] = 'admin'
                    session['user_name'] = 'Admin'
                    return redirect(url_for("admin_dashboard"))
                flash("Invalid admin credentials", "danger")
                return redirect(url_for("login"))

            else:
                flash("Please select a valid role", "warning")
                return redirect(url_for("login"))

        except Exception as e:
            flash(f"Login error: {e}", "danger")
            return redirect(url_for("login"))
        finally:
            cursor.close()
            conn.close()

    # GET
    return render_template("login.html")


# ---- Signup ----
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form.get("role")
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        extra = request.form.get("extra", "").strip() if request.form.get("extra") else None
        roll_no_form = request.form.get("roll_no", "").strip()
        year = request.form.get("year", "").strip() or None

        conn = get_connection()
        if not conn:
            flash("Database connection failed", "danger")
            return redirect(url_for("signup"))
        cursor = conn.cursor()
        try:
            if role == "teacher":
                cursor.execute("SELECT id FROM teachers WHERE email=%s", (email,))
                if cursor.fetchone():
                    flash("Teacher with this email already exists", "danger")
                    return redirect(url_for("signup"))

                cursor.execute(
                    "INSERT INTO teachers(name,email,password,status) VALUES(%s,%s,%s,'Pending')",
                    (name, email, password)
                )
                conn.commit()
                flash("Teacher registered. Please wait for admin approval.", "success")
                return redirect(url_for("login"))

            elif role == "student":
                # prefer explicit roll_no if provided
                roll_no = roll_no_form or email
                branch = extra  # use form 'extra' as branch
                # check unique
                cursor.execute("SELECT roll_no, email FROM students WHERE roll_no=%s OR email=%s", (roll_no, email))
                if cursor.fetchone():
                    flash("Student already exists", "danger")
                    return redirect(url_for("signup"))

                cursor.execute(
                    "INSERT INTO students(roll_no,name,branch,email,password,year) VALUES(%s,%s,%s,%s,%s,%s)",
                    (roll_no, name, branch, email, password, year)
                )
                conn.commit()
                flash("Student registered. You can now login.", "success")
                return redirect(url_for("login"))

            else:
                flash("Choose a valid role", "warning")
                return redirect(url_for("signup"))

        except Exception as e:
            conn.rollback()
            flash(f"Signup error: {e}", "danger")
            return redirect(url_for("signup"))
        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")


# ---- Teacher Dashboard ----
@app.route("/teacher/dashboard")
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch teacher sessions
        cursor.execute("SELECT * FROM attendance_sessions WHERE teacher_id=%s ORDER BY created_at DESC", 
                       (session['user_id'],))
        sessions = cursor.fetchall()

        # Fetch subject names (for table)
        cursor.execute("SELECT id, name FROM subjects WHERE teacher_id=%s", (session['user_id'],))
        subjects = cursor.fetchall()
        subj_map = {s['id']: s['name'] for s in subjects}
    except Exception as e:
        flash(f"Error loading dashboard: {e}", "danger")
        sessions = []
        subj_map = {}
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "dashboard_teacher.html",
        teacher_id=session['user_id'],
        teacher_name=session['user_name'],
        sessions=sessions,
        subj_map=subj_map
    )


# ---- Student Dashboard (landing) ----
@app.route("/student/dashboard")
def student_dashboard():
    if session.get('role') != 'student':
        flash("Please login as student", "warning")
        return redirect(url_for('login'))

    student_roll = session.get('user_id')
    if not student_roll:
        flash("Student id missing in session. Please login again.", "danger")
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for("login"))

    cursor = conn.cursor(dictionary=True)
    try:
        # show recent combined attendance (main attendance & session_attendance) - limited to few rows
        cursor.execute(
            "SELECT a.date AS date, COALESCE(s.name,'Unknown') AS subject, a.status AS status "
            "FROM attendance a "
            "LEFT JOIN subjects s ON a.subject_id = s.id "
            "WHERE a.student_roll_no = %s "
            "ORDER BY a.date DESC LIMIT 20",
            (student_roll,)
        )
        rows = cursor.fetchall()

        if not rows:
            cursor.execute(
                "SELECT sa.marked_at AS date, COALESCE(sub.name,'Unknown') AS subject, sa.status AS status "
                "FROM session_attendance sa "
                "LEFT JOIN attendance_sessions sess ON sa.session_id = sess.id "
                "LEFT JOIN subjects sub ON sess.subject_id = sub.id "
                "WHERE sa.student_roll_no = %s "
                "ORDER BY sa.marked_at DESC LIMIT 20",
                (student_roll,)
            )
            rows = cursor.fetchall()

        if not rows:
            flash("No recent attendance records found.", "info")

    except Exception as e:
        flash(f"Error loading attendance: {e}", "danger")
        rows = []
    finally:
        cursor.close()
        conn.close()

    return render_template("dashboard_student.html",
                           student_roll=student_roll,
                           student_name=session.get('user_name'),
                           attendance=rows)


# ---- Student -> list subjects (new) ----
@app.route("/student/subjects")
def view_subjects_student():
    if session.get('role') != 'student':
        flash("Please login as student", "warning")
        return redirect(url_for('login'))

    student_roll = session.get('user_id')
    if not student_roll:
        flash("Student id missing in session.", "danger")
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('student_dashboard'))

    cursor = conn.cursor(dictionary=True)
    try:
        # Get student's branch (so we can list subjects for their branch)
        cursor.execute("SELECT branch FROM students WHERE roll_no=%s", (student_roll,))
        s = cursor.fetchone()
        branch = s['branch'] if s else None

        if branch:
            cursor.execute("SELECT id, name, branch, teacher_id FROM subjects WHERE branch=%s", (branch,))
            subjects = cursor.fetchall()
        else:
            # fallback: show all subjects if branch not set
            cursor.execute("SELECT id, name, branch, teacher_id FROM subjects")
            subjects = cursor.fetchall()

    except Exception as e:
        flash(f"Error loading subjects: {e}", "danger")
        subjects = []
    finally:
        cursor.close()
        conn.close()

    # Template should show subjects and link to /student/attendance/subject/<id>
    return render_template("view_subjects_student.html", subjects=subjects, student_roll=student_roll)


# ---- Student -> view attendance for a specific subject (new) ----
@app.route("/student/attendance/subject/<int:subject_id>")
def student_subject_attendance(subject_id):
    if session.get('role') != 'student':
        flash("Please login as student", "warning")
        return redirect(url_for('login'))

    student_roll = session.get('user_id')
    if not student_roll:
        flash("Student id missing in session.", "danger")
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('student_dashboard'))

    cursor = conn.cursor(dictionary=True)
    try:
        # 1) regular attendance entries for this subject
        cursor.execute(
            "SELECT date AS datetime, status, 'regular' AS kind FROM attendance "
            "WHERE student_roll_no=%s AND subject_id=%s",
            (student_roll, subject_id)
        )
        regular = cursor.fetchall()

        # 2) session_attendance entries that belong to sessions of this subject
        cursor.execute(
            "SELECT sa.marked_at AS datetime, sa.status, 'session' AS kind, sa.latitude, sa.longitude "
            "FROM session_attendance sa "
            "JOIN attendance_sessions sess ON sa.session_id = sess.id "
            "WHERE sa.student_roll_no=%s AND sess.subject_id=%s",
            (student_roll, subject_id)
        )
        session_entries = cursor.fetchall()

        # 3) Subject name
        cursor.execute("SELECT name FROM subjects WHERE id=%s", (subject_id,))
        s = cursor.fetchone()
        subject_name = s['name'] if s else "Unknown Subject"

        # Combine lists and sort by datetime descending
        combined = []
        for r in regular:
            # ensure datetime type
            combined.append({
                "datetime": r['datetime'],
                "status": r['status'],
                "kind": r['kind'],
                "lat": None,
                "lon": None
            })
        for r in session_entries:
            combined.append({
                "datetime": r['datetime'],
                "status": r['status'],
                "kind": r['kind'],
                "lat": r.get('latitude'),
                "lon": r.get('longitude')
            })

        # Sort by datetime (handle None gracefully)
        combined.sort(key=lambda x: x['datetime'] or datetime.min, reverse=True)

        if not combined:
            flash("No attendance records found for this subject.", "info")

    except Exception as e:
        flash(f"Error loading subject attendance: {e}", "danger")
        combined = []
        subject_name = "Unknown Subject"
    finally:
        cursor.close()
        conn.close()

    return render_template("student_subject_attendance.html",
                           subject_id=subject_id,
                           subject_name=subject_name,
                           attendance=combined,
                           student_roll=student_roll)


# ---- Admin Dashboard (approve teachers) ----
@app.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Please login as admin", "warning")
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for("login"))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id,name,email,status FROM teachers WHERE status='Pending'")
        pending = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading pending teachers: {e}", "danger")
        pending = []
    finally:
        cursor.close()
        conn.close()

    return render_template("dashboard_admin.html", pending=pending)


@app.route("/admin_approve", methods=["GET"])
def admin_approve_page():
    # separate page to list pending teachers and approve/reject
    if session.get('role') != 'admin':
        flash("Please login as admin", "warning")
        return redirect(url_for("login"))

    conn = get_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for("login"))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id,name,email,status FROM teachers WHERE status='Pending'")
        pending = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading pending teachers: {e}", "danger")
        pending = []
    finally:
        cursor.close()
        conn.close()

    return render_template("admin_approve.html", pending=pending)


@app.route("/admin/approve/<int:teacher_id>", methods=["POST"])
def admin_approve(teacher_id):
    if session.get('role') != 'admin':
        flash("Please login as admin", "warning")
        return redirect(url_for("login"))

    action = request.form.get('action')  # 'approve' or 'reject'
    new_status = 'Approved' if action == 'approve' else 'Rejected'

    conn = get_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for("admin_dashboard"))

    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE teachers SET status=%s WHERE id=%s", (new_status, teacher_id))
        conn.commit()
        flash(f"Teacher {teacher_id} set to {new_status}", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error updating status: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_approve_page'))


# ---- Teacher mark attendance route (simple) ----
@app.route("/teacher/mark", methods=["GET", "POST"])
def teacher_mark():
    if session.get('role') != 'teacher':
        flash("Please login as teacher", "warning")
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for("teacher_dashboard"))

    cursor = conn.cursor(dictionary=True)
    try:
        if request.method == "POST":
            student_roll = request.form.get('student_roll')
            subject_id = request.form.get('subject_id')
            status = request.form.get('status')
            today = date.today()

            # prevent duplicate entry
            cursor.execute(
                "SELECT id FROM attendance WHERE student_roll_no=%s AND subject_id=%s AND date=%s",
                (student_roll, subject_id, today)
            )
            if cursor.fetchone():
                flash("Attendance already marked for today", "warning")
            else:
                cursor.execute(
                    "INSERT INTO attendance(student_roll_no,subject_id,teacher_id,date,status) VALUES(%s,%s,%s,%s,%s)",
                    (student_roll, subject_id, session.get('user_id'), today, status)
                )
                conn.commit()
                flash("Attendance marked", "success")

        # For GET: we may want to show subjects assigned to this teacher and a small form
        cursor.execute("SELECT id,name FROM subjects WHERE teacher_id=%s", (session.get('user_id'),))
        subjects = cursor.fetchall()
    except Exception as e:
        flash(f"Error in mark attendance: {e}", "danger")
        subjects = []
    finally:
        cursor.close()
        conn.close()

    return render_template("mark_attendance.html", subjects=subjects)


# ---- Teacher subjects view (used in teacher dashboard) ----
@app.route("/teacher/<int:teacher_id>/subjects")
def view_subjects_teacher(teacher_id):
    if session.get('role') not in ('teacher', 'admin'):
        flash("Please login", "warning")
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for("login"))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id,name,branch FROM subjects WHERE teacher_id=%s", (teacher_id,))
        subs = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading subjects: {e}", "danger")
        subs = []
    finally:
        cursor.close()
        conn.close()

    return render_template("view_subjects_teacher.html", subjects=subs, teacher_id=teacher_id)


# ---- Create attendance session (teacher) ----
@app.route("/teacher/session/create", methods=["GET", "POST"])
def create_session():
    if session.get('role') != 'teacher':
        flash("Please login as teacher", "warning")
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('teacher_dashboard'))

    cursor = conn.cursor(dictionary=True)
    try:
        if request.method == "POST":
            subject_id = request.form.get('subject_id')
            lat = request.form.get('latitude')
            lon = request.form.get('longitude')
            duration = int(request.form.get('duration', 10))
            radius = int(request.form.get('radius', 20))
            note = request.form.get('note','')

            if not subject_id or not lat or not lon:
                flash("Subject and location required", "danger")
                return redirect(url_for('create_session'))

            token = secrets.token_urlsafe(16)
            expires_at = datetime.utcnow() + timedelta(minutes=duration)

            cursor.execute(
                "INSERT INTO attendance_sessions(teacher_id,subject_id,token,latitude,longitude,expires_at,max_radius_m,session_note) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (session['user_id'], subject_id, token, float(lat), float(lon), expires_at, radius, note)
            )
            conn.commit()
            link = url_for('session_link', token=token, _external=True)
            flash(f"Session created. Share this link: {link}", "success")
            return redirect(url_for('teacher_dashboard'))

        # GET -> show subjects for this teacher
        cursor.execute("SELECT id, name FROM subjects WHERE teacher_id=%s", (session['user_id'],))
        subjects = cursor.fetchall()
    except Exception as e:
        conn.rollback()
        flash(f"Error creating session: {e}", "danger")
        subjects = []
    finally:
        cursor.close()
        conn.close()

    return render_template("create_session.html", subjects=subjects)


# ---- Session link page (student opens link) ----
@app.route("/session/<token>", methods=["GET"])
def session_link(token):
    conn = get_connection(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM attendance_sessions WHERE token=%s AND is_active=1", (token,))
    sess = cursor.fetchone()
    cursor.close(); conn.close()
    if not sess:
        flash("Invalid or inactive attendance link", "danger")
        return redirect(url_for('login'))

    # check expiry
    if sess['expires_at'] < datetime.utcnow():
        flash("This attendance link has expired", "warning")
        return redirect(url_for('login'))

    # show student view where they enter roll and allow location capture
    return render_template("session_page.html", sess=sess)


# ---- Session mark (student posts roll + coords) ----
@app.route("/session/<token>/mark", methods=["POST"])
def session_mark(token):
    roll_no = request.form.get('roll_no','').strip()
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    ip = request.remote_addr

    if not roll_no or not lat or not lon:
        return jsonify(success=False, msg="Missing roll or location"), 400

    conn = get_connection(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM attendance_sessions WHERE token=%s AND is_active=1", (token,))
    sess = cursor.fetchone()
    if not sess:
        cursor.close(); conn.close()
        return jsonify(success=False, msg="Invalid session"), 400

    if sess['expires_at'] < datetime.utcnow():
        cursor.close(); conn.close()
        return jsonify(success=False, msg="Session expired"), 400

    # check student exists
    cursor.execute("SELECT roll_no FROM students WHERE roll_no=%s", (roll_no,))
    if not cursor.fetchone():
        cursor.close(); conn.close()
        return jsonify(success=False, msg="Student not found"), 404

    # distance check
    dist = haversine_distance_m(sess['latitude'], sess['longitude'], float(lat), float(lon))
    if dist > sess['max_radius_m']:
        cursor.close(); conn.close()
        return jsonify(success=False, msg=f"Not in range ({int(dist)} m)"), 403

    # insert into session_attendance (unique constraint prevents duplicates)
    try:
        cursor.execute(
            "INSERT INTO session_attendance(session_id, student_roll_no, ip_addr, latitude, longitude, status) VALUES(%s,%s,%s,%s,%s,%s)",
            (sess['id'], roll_no, ip, float(lat), float(lon), 'Present')
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        cursor.close(); conn.close()
        return jsonify(success=False, msg="Already marked or DB error"), 409

    # optional: also insert into main attendance to keep daily record
    try:
        today = date.today()
        cursor.execute(
            "INSERT IGNORE INTO attendance(student_roll_no, subject_id, teacher_id, date, status) VALUES(%s,%s,%s,%s,%s)",
            (roll_no, sess['subject_id'], sess['teacher_id'], today, 'Present')
        )
        conn.commit()
    except:
        conn.rollback()

    cursor.close(); conn.close()
    return jsonify(success=True, msg="Attendance marked"), 200


# ---- Teacher view session attendees ----
@app.route("/teacher/session/<int:session_id>/view", methods=["GET"])
def teacher_view_session(session_id):
    if session.get('role') != 'teacher':
        flash("Login as teacher", "warning")
        return redirect(url_for('login'))

    conn = get_connection(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM attendance_sessions WHERE id=%s AND teacher_id=%s", (session_id, session['user_id']))
    sess = cursor.fetchone()
    if not sess:
        cursor.close(); conn.close()
        flash("Session not found", "danger")
        return redirect(url_for('teacher_dashboard'))

    cursor.execute("SELECT sa.*, s.name AS student_name FROM session_attendance sa LEFT JOIN students s ON sa.student_roll_no=s.roll_no WHERE sa.session_id=%s", (session_id,))
    attendees = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template("teacher_view_session.html", sess=sess, attendees=attendees)

    # ---- Add Subject (Admin assigns subject to teacher) ----
@app.route("/admin/add_subject", methods=["GET", "POST"])
def add_subject():
    if session.get('role') != 'admin':
        flash("Please login as admin", "warning")
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Load teachers for dropdown
    cursor.execute("SELECT id, name FROM teachers WHERE status='Approved'")
    teachers = cursor.fetchall()

    if request.method == "POST":
        name = request.form.get("name").strip()
        branch = request.form.get("branch").strip()
        teacher_id = request.form.get("teacher_id")

        if not name or not branch or not teacher_id:
            flash("All fields required", "danger")
            return redirect(url_for("add_subject"))

        cursor.execute(
            "INSERT INTO subjects(name, branch, teacher_id) VALUES(%s, %s, %s)",
            (name, branch, teacher_id)
        )
        conn.commit()
        flash("Subject added successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    cursor.close()
    conn.close()
    return render_template("add_subject.html", teachers=teachers)



# ---- Logout ----
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
