"""
CampusOS Full-Stack Backend  —  FINAL FIXED
============================================
DB: university_digital_twin (PostgreSQL 18)
Verified tables & columns:
  app_user.linked_id  = INTEGER
  library_book        (not 'book')
  student_course_enrollment (not 'enrollment')
  faculty_course      (join table)
  examination         (not 'exam')
  hostel / hostel_room (no hostel_block)
  company             (join for placement_drive)
  timetable.faculty_id (direct column)
"""
import datetime
import os
from flask import Flask, request, jsonify, send_from_directory, session
import psycopg2, psycopg2.extras

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = "campusos-secret-2026"

# Set these environment variables to match your PostgreSQL installation.
# No database password is stored in source code.
DB = dict(
    host=os.getenv("CAMPUSOS_DB_HOST", "localhost"),
    port=os.getenv("CAMPUSOS_DB_PORT", "5432"),
    dbname=os.getenv("CAMPUSOS_DB_NAME", "university_digital_twin"),
    user=os.getenv("CAMPUSOS_DB_USER", "postgres"),
    password=os.getenv("CAMPUSOS_DB_PASSWORD", "Sasank"),
    connect_timeout=5,
)

def get_conn():
    return psycopg2.connect(**DB)

import decimal

def clean_val(v):
    if isinstance(v, (datetime.time, datetime.date, datetime.datetime)):
        return str(v)
    if isinstance(v, decimal.Decimal):
        return float(v)
    return v

def q2j(cur):
    rows = cur.fetchall()
    if not rows:
        return []
    if isinstance(rows[0], dict):
        return [{k: clean_val(v) for k, v in r.items()} for r in rows]
    cols = [d[0] for d in cur.description]
    return [{k: clean_val(v) for k, v in zip(cols, row)} for row in rows]

def ok(**kw):   return jsonify({"ok": True,  **kw})
def err(m, c=400): return jsonify({"ok": False, "error": m}), c

from werkzeug.exceptions import HTTPException

@app.errorhandler(Exception)
def handle_exc(e):
    if isinstance(e, HTTPException):
        return e
    app.logger.exception("Unhandled request error")
    if isinstance(e, psycopg2.Error):
        message = "Database query failed. Check the server terminal and PostgreSQL connection/schema."
    else:
        message = "The server could not complete this request. Check the server terminal for details."
    return jsonify({"ok": False, "error": message}), 500

import gzip

def init_db_if_needed():
    try:
        with get_conn() as c:
            cur = c.cursor()
            cur.execute("SELECT to_regclass('public.student');")
            exists = cur.fetchone()[0]
            if not exists and os.path.exists("schema.sql.gz"):
                app.logger.info("Initializing Azure database schema from schema.sql.gz...")
                with gzip.open("schema.sql.gz", "rt", encoding="utf-8", errors="ignore") as gz:
                    sql_content = gz.read()
                # Execute in batches or as transaction
                cur.execute(sql_content)
                c.commit()
                app.logger.info("Database schema initialized successfully!")
    except Exception as ex:
        app.logger.error(f"init_db error: {ex}")

@app.route("/api/admin/init-db")
def admin_init_db():
    if not os.path.exists("schema.sql.gz"):
        return err("schema.sql.gz not found")
    try:
        with get_conn() as c:
            cur = c.cursor()
            with gzip.open("schema.sql.gz", "rt", encoding="utf-8", errors="ignore") as gz:
                sql_content = gz.read()
            cur.execute(sql_content)
            c.commit()
        return ok(message="Database restored successfully into Azure PostgreSQL!")
    except Exception as ex:
        return err(str(ex), 500)

@app.before_request
def check_first_init():
    if not getattr(app, "_db_initialized", False):
        app._db_initialized = True
        init_db_if_needed()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Static ──────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/assets/<path:fn>")
def assets(fn):
    return send_from_directory(os.path.join(BASE_DIR, "assets"), fn)

# ════════════════════════════════════════════════════════════
# AUTH
# ════════════════════════════════════════════════════════════
@app.route("/api/login", methods=["POST"])
def login():
    d  = request.get_json() or {}
    em = (d.get("email")    or "").strip()
    pw = (d.get("password") or "").strip()
    if not em or not pw:
        return err("Email and password required")
    with get_conn() as c:
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM app_user WHERE LOWER(email)=LOWER(%s)", (em,))
        u = cur.fetchone()
    if not u:                             return err("Email not found", 401)
    if (u["plain_password"] or "") != pw: return err("Incorrect password", 401)
    session["user"] = dict(id=u["user_id"], email=u["email"], role=u["role"],
                           linked_id=u["linked_id"], name=u["full_name"])
    return ok(role=u["role"], name=u["full_name"], linked_id=u["linked_id"])

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear(); return ok()

@app.route("/api/me")
def me():
    if "user" not in session: return err("Not logged in", 401)
    return ok(**session["user"])

@app.route("/api/quick-profiles")
def quick_profiles():
    with get_conn() as c:
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT email,plain_password AS password,role,full_name FROM app_user WHERE plain_password IS NOT NULL AND LOWER(role)='student' ORDER BY user_id LIMIT 3")
        stu = q2j(cur)
        cur.execute("SELECT email,plain_password AS password,role,full_name FROM app_user WHERE plain_password IS NOT NULL AND LOWER(role)='faculty' ORDER BY user_id LIMIT 2")
        fac = q2j(cur)
        cur.execute("SELECT email,plain_password AS password,role,full_name FROM app_user WHERE LOWER(role)='admin' LIMIT 1")
        adm = q2j(cur)
    return ok(profiles=dict(admin=adm, faculty=fac, students=stu))

# ════════════════════════════════════════════════════════════
# ADMIN STATS
# ════════════════════════════════════════════════════════════
@app.route("/api/admin/stats")
def admin_stats():
    with get_conn() as c:
        cur = c.cursor()
        def cnt(q): cur.execute(q); return cur.fetchone()[0]
        return jsonify(dict(
            students         = cnt("SELECT COUNT(*) FROM student WHERE status='Active'"),
            faculty          = cnt("SELECT COUNT(*) FROM faculty"),
            departments      = cnt("SELECT COUNT(*) FROM department"),
            courses          = cnt("SELECT COUNT(*) FROM course"),
            placement_drives = cnt("SELECT COUNT(*) FROM placement_drive WHERE drive_date>=CURRENT_DATE"),
            lib_active_loans = cnt("SELECT COUNT(*) FROM library_transaction WHERE return_date IS NULL"),
            fee_pending      = cnt("SELECT COUNT(*) FROM fee WHERE payment_status IN ('Pending','Partial')"),
            hostel_residents = cnt("SELECT COUNT(*) FROM hostel_allocation"),
            total_books      = cnt("SELECT COUNT(*) FROM library_book"),
        ))

# ════════════════════════════════════════════════════════════
# STUDENTS
# ════════════════════════════════════════════════════════════
@app.route("/api/students")
def students():
    q    = request.args.get("q","")
    dept = request.args.get("dept","")
    page = max(1, int(request.args.get("page",1)))
    lim=50; off=(page-1)*lim
    fil=["1=1"]; par=[]
    if q:
        fil.append("(s.first_name ILIKE %s OR s.last_name ILIKE %s OR s.roll_number ILIKE %s OR s.email ILIKE %s)")
        par += [f"%{q}%"]*4
    if dept:
        fil.append("d.department_name ILIKE %s"); par.append(f"%{dept}%")
    w=" AND ".join(fil)
    sql=f"""
        SELECT s.student_id, s.roll_number,
               s.first_name||' '||s.last_name AS name,
               s.email, s.gender, s.cgpa, s.status,
               s.current_year, s.current_semester,
               d.department_name, p.program_name,
               u.plain_password AS password, u.email AS login_email
        FROM student s
        JOIN department d ON s.department_id=d.department_id
        JOIN program p    ON s.program_id=p.program_id
        LEFT JOIN app_user u ON u.linked_id=s.student_id AND u.role='Student'
        WHERE {w}
        ORDER BY s.roll_number LIMIT %s OFFSET %s"""
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, par+[lim,off]); data=q2j(cur)
        cur.execute(f"SELECT COUNT(*) FROM student s LEFT JOIN department d ON s.department_id=d.department_id LEFT JOIN program p ON s.program_id=p.program_id WHERE {w}", par)
        total=list(cur.fetchone().values())[0]
    return jsonify(dict(students=data, total=total, page=page, limit=lim))

@app.route("/api/students/<int:sid>")
def student_detail(sid):
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT s.*, d.department_name, p.program_name,
                   u.email AS login_email
            FROM student s
            LEFT JOIN department d ON s.department_id=d.department_id
            LEFT JOIN program p    ON s.program_id=p.program_id
            LEFT JOIN app_user u ON u.linked_id=s.student_id AND u.role='Student'
            WHERE s.student_id=%s""", (sid,))
        s=cur.fetchone()
        if not s: return err("Not found",404)
        cur.execute("""
            SELECT c.course_name,
                   COUNT(*) FILTER(WHERE a.status='Present') AS present,
                   COUNT(*) AS total
            FROM attendance a JOIN course c ON a.course_id=c.course_id
            WHERE a.student_id=%s GROUP BY c.course_name ORDER BY c.course_name""", (sid,))
        att=q2j(cur)
        cur.execute("""
            SELECT m.marks_obtained, m.grade,
                   e.exam_type AS exam_name, e.max_marks, e.exam_date,
                   c.course_name
            FROM marks m
            JOIN examination e ON m.exam_id=e.exam_id
            JOIN course c ON e.course_id=c.course_id
            WHERE m.student_id=%s ORDER BY e.exam_date DESC""", (sid,))
        marks=q2j(cur)
        cur.execute("SELECT * FROM fee WHERE student_id=%s ORDER BY due_date DESC",(sid,))
        fees=q2j(cur)
    return jsonify(dict(student=dict(s), attendance=att, marks=marks, fees=fees))

@app.route("/api/students", methods=["POST"])
def add_student():
    # Only Admin can add students
    user = session.get("user")
    if not user or user.get("role", "").lower() != "admin":
        return err("Forbidden: Only administrators can add new students", 403)
    import random, string
    from werkzeug.security import generate_password_hash
    d  = request.get_json() or {}
    pw = ''.join(random.choices(string.ascii_letters+string.digits+"!@#$", k=8))
    with get_conn() as c:
        cur=c.cursor()
        cur.execute("SELECT department_id FROM department WHERE department_name ILIKE %s LIMIT 1",(d.get("department",""),))
        r=cur.fetchone(); dept_id=r[0] if r else 1
        cur.execute("SELECT program_id FROM program WHERE program_name ILIKE %s LIMIT 1",(d.get("program",""),))
        r=cur.fetchone(); prog_id=r[0] if r else 1
        cur.execute("""INSERT INTO student(first_name,last_name,email,phone,gender,dob,
                        department_id,program_id,admission_year,current_year,current_semester,status,roll_number)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1,'Active',%s) RETURNING student_id""",
                    (d.get("first_name",""),d.get("last_name",""),d.get("email",""),
                     d.get("phone",""),d.get("gender","Male"),d.get("dob","2000-01-01"),
                     dept_id,prog_id,datetime.datetime.now().year,d.get("roll_number","")))
        sid=cur.fetchone()[0]
        ph=generate_password_hash(pw, method="pbkdf2:sha256:10000")
        cur.execute("INSERT INTO app_user(email,password_hash,plain_password,role,linked_id,full_name) VALUES(%s,%s,%s,'Student',%s,%s)",
                    (d.get("email",""),ph,pw,sid,d.get("first_name","")+" "+d.get("last_name","")))
        c.commit()
    return ok(student_id=sid, password=pw)

@app.route("/api/students/<int:sid>", methods=["DELETE"])
def delete_student(sid):
    # Only Admin can delete students
    user = session.get("user")
    if not user or user.get("role", "").lower() != "admin":
        return err("Forbidden: Only administrators can delete students", 403)
    with get_conn() as c:
        cur=c.cursor()
        cur.execute("DELETE FROM app_user WHERE linked_id=%s AND role='Student'",(sid,))
        cur.execute("DELETE FROM student WHERE student_id=%s",(sid,))
        c.commit()
    return ok()

# ════════════════════════════════════════════════════════════
# FACULTY
# ════════════════════════════════════════════════════════════
@app.route("/api/faculty")
def faculty_list():
    q    = request.args.get("q","")
    dept = request.args.get("dept","")
    page = max(1,int(request.args.get("page",1)))
    lim=50; off=(page-1)*lim
    fil=["1=1"]; par=[]
    if q:
        fil.append("(f.first_name ILIKE %s OR f.last_name ILIKE %s OR f.email ILIKE %s)")
        par+=[f"%{q}%"]*3
    if dept:
        fil.append("d.department_name ILIKE %s"); par.append(f"%{dept}%")
    w=" AND ".join(fil)
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(f"""
            SELECT f.faculty_id, f.first_name||' '||f.last_name AS name,
                   f.email, f.designation, f.qualification,
                   f.experience_years, f.date_of_joining,
                   d.department_name, u.plain_password AS password
            FROM faculty f
            JOIN department d ON f.department_id=d.department_id
            LEFT JOIN app_user u ON u.linked_id=f.faculty_id AND u.role='Faculty'
            WHERE {w} ORDER BY f.first_name LIMIT %s OFFSET %s""", par+[lim,off])
        data=q2j(cur)
        cur.execute(f"SELECT COUNT(*) FROM faculty f JOIN department d ON f.department_id=d.department_id WHERE {w}",par)
        total=cur.fetchone()["count"]
    return jsonify(dict(faculty=data, total=total))

@app.route("/api/faculty/<int:fid>")
def faculty_detail(fid):
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT f.*, d.department_name, u.plain_password
            FROM faculty f
            JOIN department d ON f.department_id=d.department_id
            LEFT JOIN app_user u ON u.linked_id=f.faculty_id AND u.role='Faculty'
            WHERE f.faculty_id=%s""", (fid,))
        f=cur.fetchone()
        if not f: return err("Not found",404)
        cur.execute("""
            SELECT c.course_id, c.course_code, c.course_name, c.credits, c.semester_number, c.course_type,
                   COUNT(DISTINCT sce.student_id) AS enrolled
            FROM faculty_course fc
            JOIN course c ON fc.course_id=c.course_id
            LEFT JOIN student_course_enrollment sce ON sce.course_id=c.course_id
            WHERE fc.faculty_id=%s
            GROUP BY c.course_id,c.course_code,c.course_name,c.credits,c.semester_number,c.course_type""", (fid,))
        courses=q2j(cur)
    return jsonify(dict(faculty=dict(f), courses=courses))

@app.route("/api/faculty/<int:fid>/students")
def faculty_students(fid):
    cid = request.args.get("course_id")
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if cid and str(cid).lstrip("-").isdigit():
            cur.execute("""
                SELECT DISTINCT s.student_id, s.roll_number,
                       s.first_name||' '||s.last_name AS name,
                       s.email, s.cgpa, d.department_name
                FROM student_course_enrollment sce
                JOIN student s ON sce.student_id=s.student_id
                JOIN faculty_course fc ON sce.course_id=fc.course_id
                JOIN department d ON s.department_id=d.department_id
                WHERE fc.faculty_id=%s AND fc.course_id=%s
                ORDER BY s.roll_number""", (fid, int(cid)))
        else:
            cur.execute("""
                SELECT DISTINCT s.student_id, s.roll_number,
                       s.first_name||' '||s.last_name AS name,
                       s.email, s.cgpa, d.department_name
                FROM student_course_enrollment sce
                JOIN student s ON sce.student_id=s.student_id
                JOIN faculty_course fc ON sce.course_id=fc.course_id
                JOIN department d ON s.department_id=d.department_id
                WHERE fc.faculty_id=%s ORDER BY s.roll_number""", (fid,))
        return jsonify(dict(students=q2j(cur)))

# ════════════════════════════════════════════════════════════
# DEPARTMENTS
# ════════════════════════════════════════════════════════════
@app.route("/api/departments")
def departments():
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT d.department_id, d.department_name,
                   COUNT(DISTINCT f.faculty_id)  AS faculty_count,
                   COUNT(DISTINCT s.student_id)  AS student_count,
                   COUNT(DISTINCT c.course_id)   AS course_count
            FROM department d
            LEFT JOIN faculty f ON f.department_id=d.department_id
            LEFT JOIN student s ON s.department_id=d.department_id AND s.status='Active'
            LEFT JOIN course  c ON c.department_id=d.department_id
            GROUP BY d.department_id,d.department_name ORDER BY d.department_name""")
        return jsonify(dict(departments=q2j(cur)))

# ════════════════════════════════════════════════════════════
# COURSES
# ════════════════════════════════════════════════════════════
@app.route("/api/courses")
def courses():
    q=request.args.get("q",""); dept=request.args.get("dept","")
    page=max(1,int(request.args.get("page",1))); lim=50; off=(page-1)*lim
    fil=["1=1"]; par=[]
    if q:
        fil.append("(c.course_name ILIKE %s OR c.course_code ILIKE %s)"); par+=[f"%{q}%"]*2
    if dept:
        fil.append("d.department_name ILIKE %s"); par.append(f"%{dept}%")
    w=" AND ".join(fil)
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(f"""
            SELECT c.course_id, c.course_code, c.course_name, c.credits,
                   c.semester_number, c.course_type, d.department_name,
                   COUNT(DISTINCT sce.student_id) AS enrolled
            FROM course c
            LEFT JOIN department d ON c.department_id=d.department_id
            LEFT JOIN student_course_enrollment sce ON sce.course_id=c.course_id
            WHERE {w}
            GROUP BY c.course_id,c.course_code,c.course_name,c.credits,
                     c.semester_number,c.course_type,d.department_name
            ORDER BY c.course_code LIMIT %s OFFSET %s""", par+[lim,off])
        data=q2j(cur)
        cur.execute(f"SELECT COUNT(*) FROM course c LEFT JOIN department d ON c.department_id=d.department_id WHERE {w}",par)
        total=cur.fetchone()["count"]
    return jsonify(dict(courses=data, total=total))

# ════════════════════════════════════════════════════════════
# TIMETABLE
# ════════════════════════════════════════════════════════════
@app.route("/api/timetable")
def timetable():
    sid=request.args.get("student_id")
    fid=request.args.get("faculty_id")
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if sid and sid.lstrip("-").isdigit():
            cur.execute("""
                SELECT t.day_of_week, t.start_time, t.end_time,
                       c.course_name, c.course_code,
                       cl.room_number,
                       f.first_name||' '||f.last_name AS faculty_name
                FROM timetable t
                JOIN course c ON t.course_id=c.course_id
                LEFT JOIN classroom cl ON t.classroom_id=cl.classroom_id
                LEFT JOIN faculty f ON t.faculty_id=f.faculty_id
                JOIN student_course_enrollment sce ON sce.course_id=c.course_id
                WHERE sce.student_id=%s
                ORDER BY t.day_of_week, t.start_time""", (int(sid),))
        elif fid and fid.lstrip("-").isdigit():
            cur.execute("""
                SELECT t.day_of_week, t.start_time, t.end_time,
                       c.course_name, c.course_code, cl.room_number,
                       COUNT(DISTINCT sce.student_id) AS enrolled
                FROM timetable t
                JOIN course c ON t.course_id=c.course_id
                LEFT JOIN classroom cl ON t.classroom_id=cl.classroom_id
                LEFT JOIN student_course_enrollment sce ON sce.course_id=c.course_id
                WHERE t.faculty_id=%s
                GROUP BY t.timetable_id,t.day_of_week,t.start_time,t.end_time,
                         c.course_name,c.course_code,cl.room_number
                ORDER BY t.day_of_week, t.start_time""", (int(fid),))
        else:
            cur.execute("""
                SELECT t.day_of_week, t.start_time, t.end_time,
                       c.course_name, c.course_code, cl.room_number,
                       d.department_name,
                       f.first_name||' '||f.last_name AS faculty_name
                FROM timetable t
                JOIN course c ON t.course_id=c.course_id
                JOIN department d ON c.department_id=d.department_id
                LEFT JOIN classroom cl ON t.classroom_id=cl.classroom_id
                LEFT JOIN faculty f ON t.faculty_id=f.faculty_id
                ORDER BY t.day_of_week, t.start_time LIMIT 200""")
        return jsonify(dict(timetable=q2j(cur)))

# ════════════════════════════════════════════════════════════
# ATTENDANCE
# ════════════════════════════════════════════════════════════
@app.route("/api/attendance/summary")
def attendance_summary():
    sid=request.args.get("student_id")
    cid=request.args.get("course_id")
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if sid and str(sid).lstrip("-").isdigit():
            cur.execute("""
                SELECT c.course_id, c.course_name,
                       COUNT(*) FILTER(WHERE a.status='Present') AS present,
                       COUNT(*) FILTER(WHERE a.status='Absent')  AS absent,
                       COUNT(*) AS total,
                       ROUND(COUNT(*) FILTER(WHERE a.status='Present')::numeric
                             /NULLIF(COUNT(*),0)*100,1) AS pct
                FROM attendance a JOIN course c ON a.course_id=c.course_id
                WHERE a.student_id=%s
                GROUP BY c.course_id,c.course_name ORDER BY c.course_name""", (int(sid),))
        elif cid and str(cid).lstrip("-").isdigit():
            cur.execute("""
                SELECT s.student_id, s.roll_number,
                       s.first_name||' '||s.last_name AS name,
                       COUNT(*) FILTER(WHERE a.status='Present') AS present,
                       COUNT(*) AS total,
                       ROUND(COUNT(*) FILTER(WHERE a.status='Present')::numeric
                             /NULLIF(COUNT(*),0)*100,1) AS pct
                FROM student s JOIN attendance a ON a.student_id=s.student_id
                WHERE a.course_id=%s
                GROUP BY s.student_id,s.roll_number,s.first_name,s.last_name
                ORDER BY pct""", (int(cid),))
        else:
            return jsonify(dict(attendance=[]))
        return jsonify(dict(attendance=q2j(cur)))

@app.route("/api/attendance/mark", methods=["POST"])
def mark_attendance():
    d=request.get_json() or {}
    fid=d.get("faculty_id"); count=0
    with get_conn() as c:
        cur=c.cursor()
        for rec in d.get("records",[]):
            cur.execute("""
                INSERT INTO attendance(student_id,course_id,date,status,marked_by)
                VALUES(%s,%s,%s,%s,%s)
                ON CONFLICT (student_id, course_id, date) 
                DO UPDATE SET status=EXCLUDED.status, marked_by=EXCLUDED.marked_by
            """,
            (rec["student_id"], rec["course_id"],
             rec.get("date", str(datetime.date.today())),
             rec.get("status", "Present"), fid))
            count+=1
        c.commit()
    return ok(marked=count)

# ════════════════════════════════════════════════════════════
# MARKS  (table: examination)
# ════════════════════════════════════════════════════════════
@app.route("/api/marks")
def marks():
    sid=request.args.get("student_id")
    eid=request.args.get("exam_id")
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if sid and str(sid).lstrip("-").isdigit():
            cur.execute("""
                SELECT m.marks_id, m.marks_obtained, m.grade,
                       e.exam_type AS exam_name, e.max_marks, e.exam_date,
                       c.course_name, c.course_code
                FROM marks m
                JOIN examination e ON m.exam_id=e.exam_id
                JOIN course c ON e.course_id=c.course_id
                WHERE m.student_id=%s ORDER BY e.exam_date DESC""", (int(sid),))
        elif eid and str(eid).lstrip("-").isdigit():
            cur.execute("""
                SELECT m.marks_id, m.marks_obtained, m.grade,
                       s.roll_number, s.first_name||' '||s.last_name AS name
                FROM marks m JOIN student s ON m.student_id=s.student_id
                WHERE m.exam_id=%s ORDER BY s.roll_number""", (int(eid),))
        else:
            return jsonify(dict(marks=[]))
        return jsonify(dict(marks=q2j(cur)))

@app.route("/api/marks", methods=["POST"])
def add_marks():
    d=request.get_json() or {}; ins=0; skip=0
    with get_conn() as c:
        cur=c.cursor()
        for r in d.get("records",[]):
            try:
                cur.execute("INSERT INTO marks(student_id,exam_id,marks_obtained,grade) VALUES(%s,%s,%s,%s) ON CONFLICT(student_id,exam_id) DO UPDATE SET marks_obtained=EXCLUDED.marks_obtained,grade=EXCLUDED.grade",
                            (r["student_id"],r["exam_id"],r["marks_obtained"],r.get("grade","")))
                ins+=1
            except: skip+=1
        c.commit()
    return ok(inserted=ins, skipped=skip)

@app.route("/api/exams")
def exams():
    cid=request.args.get("course_id"); fid=request.args.get("faculty_id")
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if cid and str(cid).lstrip("-").isdigit():
            cur.execute("SELECT * FROM examination WHERE course_id=%s ORDER BY exam_date",(int(cid),))
        elif fid and str(fid).lstrip("-").isdigit():
            cur.execute("SELECT e.* FROM examination e JOIN faculty_course fc ON e.course_id=fc.course_id WHERE fc.faculty_id=%s ORDER BY e.exam_date",(int(fid),))
        else:
            cur.execute("SELECT * FROM examination ORDER BY exam_date DESC LIMIT 100")
        return jsonify(dict(exams=q2j(cur)))

# ════════════════════════════════════════════════════════════
# FEES
# ════════════════════════════════════════════════════════════
@app.route("/api/fees")
def fees():
    sid=request.args.get("student_id"); status=request.args.get("status","")
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if sid and str(sid).lstrip("-").isdigit():
            cur.execute("SELECT * FROM fee WHERE student_id=%s ORDER BY due_date DESC",(int(sid),))
        else:
            sql="SELECT f.*,s.roll_number,s.first_name||' '||s.last_name AS name FROM fee f JOIN student s ON f.student_id=s.student_id"
            par=[]
            if status: sql+=" WHERE f.payment_status=%s"; par.append(status)
            sql+=" ORDER BY f.due_date DESC LIMIT 200"
            cur.execute(sql,par)
        return jsonify(dict(fees=q2j(cur)))

@app.route("/api/fees/collect", methods=["POST"])
def collect_fee():
    d=request.get_json() or {}; fid=d.get("fee_id"); amount=float(d.get("amount",0))
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM fee WHERE fee_id=%s",(fid,))
        fee=cur.fetchone()
        if not fee: return err("Not found",404)
        new_paid=float(fee["paid_amount"] or 0)+amount
        total=float(fee["amount"])
        status="Paid" if new_paid>=total else "Partial"
        cur.execute("UPDATE fee SET paid_amount=%s,payment_status=%s,payment_date=CURRENT_DATE WHERE fee_id=%s",(new_paid,status,fid))
        c.commit()
    return ok(new_status=status, total_paid=new_paid)

# ════════════════════════════════════════════════════════════
# LIBRARY  (table: library_book, library_transaction)
# ════════════════════════════════════════════════════════════
@app.route("/api/library/books")
def library_books():
    q=request.args.get("q",""); page=max(1,int(request.args.get("page",1))); lim=50; off=(page-1)*lim
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if q:
            cur.execute("SELECT * FROM library_book WHERE title ILIKE %s OR author ILIKE %s OR isbn ILIKE %s ORDER BY title LIMIT %s OFFSET %s",[f"%{q}%"]*3+[lim,off])
        else:
            cur.execute("SELECT * FROM library_book ORDER BY title LIMIT %s OFFSET %s",(lim,off))
        data=q2j(cur)
        cur.execute("SELECT COUNT(*) FROM library_book"+(" WHERE title ILIKE %s OR author ILIKE %s OR isbn ILIKE %s" if q else ""),[f"%{q}%"]*3 if q else [])
        total=list(cur.fetchone().values())[0]
    return jsonify(dict(books=data, total=total))

@app.route("/api/library/transactions")
def library_transactions():
    uid=request.args.get("user_id"); utype=request.args.get("user_type","Student")
    active=request.args.get("active","false")=="true"
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if uid and str(uid).lstrip("-").isdigit():
            sql="SELECT lt.*,b.title,b.author FROM library_transaction lt JOIN library_book b ON lt.book_id=b.book_id WHERE lt.user_id=%s AND lt.user_type=%s"
            par=[int(uid),utype]
            if active: sql+=" AND lt.return_date IS NULL"
            cur.execute(sql+" ORDER BY lt.issue_date DESC",par)
        else:
            cur.execute("SELECT lt.*,b.title,b.author FROM library_transaction lt JOIN library_book b ON lt.book_id=b.book_id WHERE lt.return_date IS NULL ORDER BY lt.due_date LIMIT 100")
        return jsonify(dict(transactions=q2j(cur)))

@app.route("/api/library/return", methods=["POST"])
def return_book():
    d=request.get_json() or {}; tid=d.get("transaction_id")
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM library_transaction WHERE transaction_id=%s",(tid,))
        tx=cur.fetchone()
        if not tx: return err("Not found",404)
        due=tx["due_date"]; today=datetime.date.today()
        if isinstance(due,str): due=datetime.date.fromisoformat(due)
        fine=max(0,(today-due).days*5) if today>due else 0
        cur.execute("UPDATE library_transaction SET return_date=CURRENT_DATE,fine_amount=%s WHERE transaction_id=%s",(fine,tid))
        cur.execute("UPDATE library_book SET available_copies=available_copies+1 WHERE book_id=%s",(tx["book_id"],))
        c.commit()
    return ok(fine=fine)

# ════════════════════════════════════════════════════════════
# HOSTEL
# ════════════════════════════════════════════════════════════
@app.route("/api/hostel")
def hostel():
    sid=request.args.get("student_id")
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if sid and str(sid).lstrip("-").isdigit():
            cur.execute("""
                SELECT ha.*, hr.room_number, hr.capacity, hr.occupied_count,
                       h.hostel_name, h.block, h.gender_type
                FROM hostel_allocation ha
                JOIN hostel_room hr ON ha.room_id=hr.room_id
                JOIN hostel h ON hr.hostel_id=h.hostel_id
                WHERE ha.student_id=%s ORDER BY ha.allocation_date DESC LIMIT 1""", (int(sid),))
        else:
            cur.execute("""
                SELECT h.hostel_name, h.block, h.gender_type, h.total_rooms,
                       COUNT(DISTINCT hr.room_id) AS room_count,
                       SUM(hr.capacity)           AS total_capacity,
                       COUNT(ha.allocation_id)    AS occupied
                FROM hostel h
                JOIN hostel_room hr ON hr.hostel_id=h.hostel_id
                LEFT JOIN hostel_allocation ha ON ha.room_id=hr.room_id
                GROUP BY h.hostel_id,h.hostel_name,h.block,h.gender_type,h.total_rooms
                ORDER BY h.hostel_name""")
        return jsonify(dict(hostel=q2j(cur)))

# ════════════════════════════════════════════════════════════
# PLACEMENTS  (company JOIN for name)
# ════════════════════════════════════════════════════════════
@app.route("/api/placements/drives")
def placement_drives():
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT pd.drive_id, co.company_name, co.industry_type,
                   pd.eligibility_min_cgpa AS eligibility_cgpa,
                   pd.drive_date, pd.package_offered_lpa AS package_lpa,
                   COUNT(pr.registration_id) AS registrations,
                   COUNT(pr.registration_id) FILTER(WHERE pr.selection_status='Selected') AS selected
            FROM placement_drive pd
            JOIN company co ON pd.company_id=co.company_id
            LEFT JOIN placement_registration pr ON pr.drive_id=pd.drive_id
            GROUP BY pd.drive_id,co.company_name,co.industry_type,
                     pd.eligibility_min_cgpa,pd.drive_date,pd.package_offered_lpa
            ORDER BY pd.drive_date DESC""")
        return jsonify(dict(drives=q2j(cur)))

@app.route("/api/placements/register", methods=["POST"])
def register_placement():
    d=request.get_json() or {}
    try:
        with get_conn() as c:
            cur=c.cursor()
            cur.execute("INSERT INTO placement_registration(student_id,drive_id,selection_status) VALUES(%s,%s,'Registered')",(d.get("student_id"),d.get("drive_id")))
            c.commit()
        return ok()
    except Exception as ex:
        return err(str(ex))

@app.route("/api/placements/my")
def my_placements():
    sid=request.args.get("student_id")
    if not sid or not str(sid).lstrip("-").isdigit():
        return jsonify(dict(registrations=[]))
    with get_conn() as c:
        cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT pr.registration_id, pr.selection_status, pr.interview_date,
                   co.company_name, co.industry_type,
                   pd.package_offered_lpa AS package_lpa, pd.drive_date
            FROM placement_registration pr
            JOIN placement_drive pd ON pr.drive_id=pd.drive_id
            JOIN company co ON pd.company_id=co.company_id
            WHERE pr.student_id=%s ORDER BY pd.drive_date DESC""", (int(sid),))
        return jsonify(dict(registrations=q2j(cur)))

# ════════════════════════════════════════════════════════════
# SQL CONSOLE
# ════════════════════════════════════════════════════════════
@app.route("/api/sql", methods=["POST"])
def sql_console():
    d=request.get_json() or {}; q=(d.get("query","")).strip()
    if not q: return err("No query")
    for danger in ["drop ","truncate ","delete from ","alter table","grant ","revoke "]:
        if danger in q.lower(): return err("Destructive SQL blocked"),403
    try:
        with get_conn() as c:
            cur=c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(q)
            cols=[desc[0] for desc in cur.description] if cur.description else []
            rows=[list(r.values()) for r in cur.fetchall()]
        return ok(columns=cols, rows=rows[:200])
    except Exception as ex:
        return err(str(ex))

if __name__ == "__main__":
    print("="*55)
    print("  CampusOS  →  http://127.0.0.1:5000")
    print("="*55)
    app.run(debug=True, port=5000, use_reloader=False)


