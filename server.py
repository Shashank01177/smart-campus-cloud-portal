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

# ════════════════════════════════════════════════════════════
# UNIVERSAL AI INLINE SQL TRANSLATOR
# ════════════════════════════════════════════════════════════
SCHEMA_PROMPT = """You are an expert PostgreSQL 18 DBA for the university_digital_twin database.
The database schema has these tables:
1. department (department_id, department_name, department_code, hod_id, established_year, contact_email)
2. program (program_id, department_id, program_name, degree_level, duration_years, total_semesters)
3. faculty (faculty_id, department_id, first_name, last_name, email, phone, designation, joining_date, qualification, specialization, salary)
4. student (student_id, roll_number, first_name, last_name, email, phone, gender, dob, department_id, program_id, admission_year, current_year, current_semester, cgpa, status)
5. course (course_id, course_code, course_name, department_id, program_id, credits, semester_number, course_type)
6. faculty_course (allocation_id, faculty_id, course_id, academic_year, semester_type)
7. student_course_enrollment (enrollment_id, student_id, course_id, enrollment_date, status)
8. attendance (attendance_id, student_id, course_id, date, status ['Present', 'Absent', 'On Duty'], marked_by)
9. examination (exam_id, course_id, exam_type, exam_date, max_marks, weightage_percent)
10. marks (mark_id, student_id, exam_id, marks_obtained, grade)
11. fee (fee_id, student_id, fee_type, amount, due_date, payment_status ['Paid', 'Pending', 'Overdue'], paid_date)
12. hostel (hostel_id, hostel_name, gender ['Boys', 'Girls'], total_capacity, warden_name, warden_phone)
13. hostel_room (room_id, hostel_id, room_number, capacity, current_occupancy, floor_number)
14. hostel_allocation (allocation_id, student_id, room_id, allocation_date, vacation_date)
15. library_book (book_id, isbn, title, author, department_id, total_copies, available_copies)
16. library_transaction (transaction_id, book_id, student_id, issue_date, due_date, return_date, fine_amount)
17. company (company_id, company_name, industry_type, contact_email, tier ['Dream', 'Super Dream', 'Regular'])
18. placement_drive (drive_id, company_id, drive_date, package_lpa, min_cgpa, venue)
19. placement_registration (registration_id, drive_id, student_id, status ['Applied', 'Shortlisted', 'Interviewed', 'Offered', 'Rejected'])
20. app_user (user_id, email, password_hash, plain_password, role ['Admin', 'Faculty', 'Student'], linked_id, full_name)

Translate the user's natural language question into a clean, correct PostgreSQL SELECT query.
Output ONLY the raw SQL code. No markdown code blocks, no explanation, no backticks."""

def _call_gemini_api(prompt, api_key):
    import urllib.request, json
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": f"{SCHEMA_PROMPT}\n\nQuestion: {prompt}"}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 350}
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            text = re.sub(r"^```(?:sql)?", "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r"```$", "", text).strip()
            return text
    except Exception:
        return None

def universal_nlp_to_sql(prompt):
    import re
    p = prompt.lower().strip()

    # 1. Salary Queries
    if "salary" in p:
        if "second highest" in p or "2nd highest" in p:
            return "SELECT faculty_id, first_name || ' ' || last_name AS faculty_name, designation, salary, department_id FROM faculty ORDER BY salary DESC OFFSET 1 LIMIT 1;"
        if "third highest" in p or "3rd highest" in p:
            return "SELECT faculty_id, first_name || ' ' || last_name AS faculty_name, designation, salary, department_id FROM faculty ORDER BY salary DESC OFFSET 2 LIMIT 1;"
        if "lowest" in p or "min" in p:
            return "SELECT faculty_id, first_name || ' ' || last_name AS faculty_name, designation, salary, department_id FROM faculty ORDER BY salary ASC LIMIT 1;"
        if "highest" in p or "max" in p or "top" in p:
            return "SELECT faculty_id, first_name || ' ' || last_name AS faculty_name, designation, salary, department_id FROM faculty ORDER BY salary DESC LIMIT 1;"
        if "average" in p or "avg" in p:
            return "SELECT d.department_name, COUNT(f.faculty_id) AS faculty_count, ROUND(AVG(f.salary), 2) AS avg_salary FROM faculty f JOIN department d ON f.department_id = d.department_id GROUP BY d.department_name ORDER BY avg_salary DESC;"
        return "SELECT faculty_id, first_name || ' ' || last_name AS faculty_name, designation, salary FROM faculty ORDER BY salary DESC LIMIT 10;"

    # 2. Only one student
    if "only one student" in p or "1 student" in p or "one student" in p:
        if "department" in p:
            return "SELECT d.department_name, COUNT(s.student_id) AS student_count FROM department d JOIN student s ON d.department_id = s.department_id GROUP BY d.department_id, d.department_name HAVING COUNT(s.student_id) = 1;"
        elif "faculty" in p:
            return "SELECT f.first_name || ' ' || f.last_name AS faculty_name, c.course_name, COUNT(sce.student_id) AS student_count FROM faculty f JOIN faculty_course fc ON f.faculty_id = fc.faculty_id JOIN course c ON fc.course_id = c.course_id JOIN student_course_enrollment sce ON c.course_id = sce.course_id GROUP BY f.faculty_id, f.first_name, f.last_name, c.course_name HAVING COUNT(sce.student_id) = 1;"
        else:
            return "SELECT c.course_code, c.course_name, COUNT(sce.student_id) AS enrolled_students FROM course c JOIN student_course_enrollment sce ON c.course_id = sce.course_id GROUP BY c.course_id, c.course_code, c.course_name HAVING COUNT(sce.student_id) = 1;"

    # 3. Faculty course load: faculty > N courses / subjects
    m = re.search(r"faculty\s*(>|<|>=|<=|=)\s*(\d+)\s*(?:courses?|subjects?)?", p)
    if m and ("course" in p or "subject" in p or ("student" not in p and m.group(2))):
        return f"SELECT f.faculty_id, f.first_name || ' ' || f.last_name AS faculty_name, f.designation, d.department_name, COUNT(fc.course_id) AS total_courses_taught FROM faculty f JOIN department d ON f.department_id = d.department_id JOIN faculty_course fc ON f.faculty_id = fc.faculty_id GROUP BY f.faculty_id, f.first_name, f.last_name, f.designation, d.department_name HAVING COUNT(fc.course_id) {m.group(1)} {m.group(2)} ORDER BY total_courses_taught DESC;"

    # 4. Faculty student load: faculty > N students
    m = re.search(r"faculty\s*(>|<|>=|<=|=)\s*(\d+)\s*students?", p)
    if m:
        return f"SELECT f.faculty_id, f.first_name || ' ' || f.last_name AS faculty_name, f.designation, d.department_name, COUNT(DISTINCT sce.student_id) AS total_students_taught FROM faculty f JOIN department d ON f.department_id = d.department_id JOIN faculty_course fc ON f.faculty_id = fc.faculty_id JOIN student_course_enrollment sce ON fc.course_id = sce.course_id GROUP BY f.faculty_id, f.first_name, f.last_name, f.designation, d.department_name HAVING COUNT(DISTINCT sce.student_id) {m.group(1)} {m.group(2)} ORDER BY total_students_taught DESC;"

    # 5. Faculty without courses / unassigned
    if "faculty" in p and ("no course" in p or "not teaching" in p or "unassigned" in p or "without course" in p):
        return "SELECT f.faculty_id, f.first_name || ' ' || f.last_name AS faculty_name, f.designation, d.department_name FROM faculty f JOIN department d ON f.department_id = d.department_id LEFT JOIN faculty_course fc ON f.faculty_id = fc.faculty_id WHERE fc.allocation_id IS NULL;"

    # 6. Faculty list with courses
    if "faculty" in p and ("courses" in p or "subjects" in p or "teaching" in p or "teach" in p or "who teaches" in p):
        return "SELECT f.first_name || ' ' || f.last_name AS faculty_name, f.designation, d.department_name, c.course_code, c.course_name, c.credits FROM faculty f JOIN department d ON f.department_id = d.department_id JOIN faculty_course fc ON f.faculty_id = fc.faculty_id JOIN course c ON fc.course_id = c.course_id ORDER BY d.department_name, faculty_name;"

    # 7. Student CGPA queries
    m = re.search(r"cgpa\s*(>|<|>=|<=|=)\s*(\d+(?:\.\d+)?)", p) or re.search(r"students?\s*(>|<|>=|<=|=)\s*(\d+(?:\.\d+)?)\s*cgpa", p)
    if m:
        return f"SELECT roll_number, first_name || ' ' || last_name AS student_name, current_semester, cgpa, status FROM student WHERE cgpa {m.group(1)} {m.group(2)} AND status = 'Active' ORDER BY cgpa DESC;"
    if "student" in p and ("topper" in p or "highest cgpa" in p or "top student" in p or "best student" in p):
        return "SELECT roll_number, first_name || ' ' || last_name AS student_name, d.department_name, cgpa FROM student s JOIN department d ON s.department_id = d.department_id WHERE s.status = 'Active' ORDER BY s.cgpa DESC LIMIT 5;"

    # 8. Attendance queries
    if "attendance" in p:
        m = re.search(r"attendance\s*(>|<|>=|<=|=)\s*(\d+)%?", p)
        if m:
            return f"SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, c.course_code, c.course_name, COUNT(a.attendance_id) AS total_lectures, SUM(CASE WHEN a.status IN ('Present', 'On Duty') THEN 1 ELSE 0 END) AS attended_lectures, ROUND(100.0 * SUM(CASE WHEN a.status IN ('Present', 'On Duty') THEN 1 ELSE 0 END) / COUNT(a.attendance_id), 2) AS attendance_pct FROM student s JOIN attendance a ON s.student_id = a.student_id JOIN course c ON a.course_id = c.course_id GROUP BY s.student_id, s.roll_number, s.first_name, s.last_name, c.course_code, c.course_name HAVING (100.0 * SUM(CASE WHEN a.status IN ('Present', 'On Duty') THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) {m.group(1)} {m.group(2)} ORDER BY attendance_pct ASC;"
        if "shortage" in p or "below 75" in p or "less than 75" in p or "< 75" in p:
            return "SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, c.course_code, c.course_name, COUNT(a.attendance_id) AS total_lectures, SUM(CASE WHEN a.status IN ('Present', 'On Duty') THEN 1 ELSE 0 END) AS attended, ROUND(100.0 * SUM(CASE WHEN a.status IN ('Present', 'On Duty') THEN 1 ELSE 0 END) / COUNT(a.attendance_id), 2) AS pct FROM student s JOIN attendance a ON s.student_id = a.student_id JOIN course c ON a.course_id = c.course_id GROUP BY s.student_id, s.roll_number, s.first_name, s.last_name, c.course_code, c.course_name HAVING (100.0 * SUM(CASE WHEN a.status IN ('Present', 'On Duty') THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) < 75.0 ORDER BY pct ASC;"
        return "SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, c.course_code, COUNT(a.attendance_id) AS total_sessions, ROUND(100.0 * SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) / COUNT(a.attendance_id), 2) AS attendance_pct FROM student s JOIN attendance a ON s.student_id = a.student_id JOIN course c ON a.course_id = c.course_id GROUP BY s.student_id, s.roll_number, s.first_name, s.last_name, c.course_code;"

    # 9. Marks & Exam Toppers
    if "marks" in p or "exam" in p or "topper" in p or "grade" in p or "score" in p:
        if "topper" in p or "highest mark" in p or "highest score" in p:
            return "WITH ranked_scores AS (SELECT c.course_code, c.course_name, s.roll_number, s.first_name || ' ' || s.last_name AS student_name, m.marks_obtained, DENSE_RANK() OVER (PARTITION BY c.course_id ORDER BY m.marks_obtained DESC) AS course_rank FROM marks m JOIN examination e ON m.exam_id = e.exam_id JOIN course c ON e.course_id = c.course_id JOIN student s ON m.student_id = s.student_id) SELECT course_code, course_name, roll_number, student_name, marks_obtained AS topper_marks FROM ranked_scores WHERE course_rank = 1;"
        if "fail" in p:
            return "SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, c.course_code, c.course_name, m.marks_obtained, e.max_marks, m.grade FROM student s JOIN marks m ON s.student_id = m.student_id JOIN examination e ON m.exam_id = e.exam_id JOIN course c ON e.course_id = c.course_id WHERE m.marks_obtained < 40 OR m.grade = 'F';"
        return "SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, c.course_code, e.exam_type, m.marks_obtained, e.max_marks, m.grade FROM student s JOIN marks m ON s.student_id = m.student_id JOIN examination e ON m.exam_id = e.exam_id JOIN course c ON e.course_id = c.course_id LIMIT 20;"

    # 10. Fees & Dues
    if "fee" in p or "due" in p or "unpaid" in p or "defaulter" in p:
        m = re.search(r"fee(?:s)?.*?(>|<|>=|<=|=)\s*(\d+)", p)
        if m:
            return f"SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, d.department_name, SUM(f.amount) AS total_pending_due FROM student s JOIN department d ON s.department_id = d.department_id JOIN fee f ON s.student_id = f.student_id WHERE f.payment_status IN ('Pending', 'Overdue') GROUP BY s.roll_number, student_name, d.department_name HAVING SUM(f.amount) {m.group(1)} {m.group(2)} ORDER BY total_pending_due DESC;"
        if "pending" in p or "unpaid" in p or "defaulter" in p or "overdue" in p:
            return "SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, d.department_name, SUM(f.amount) AS total_due FROM student s JOIN department d ON s.department_id = d.department_id JOIN fee f ON s.student_id = f.student_id WHERE f.payment_status IN ('Pending', 'Overdue') GROUP BY s.roll_number, student_name, d.department_name ORDER BY total_due DESC;"
        return "SELECT fee_type, COUNT(*) AS count, SUM(amount) AS total_amount, payment_status FROM fee GROUP BY fee_type, payment_status;"

    # 11. Hostel Queries
    if "hostel" in p or "room" in p:
        if "vacan" in p or "available" in p or "empty" in p:
            return "SELECT h.hostel_name, hr.room_number, hr.floor_number, hr.capacity, hr.current_occupancy, (hr.capacity - hr.current_occupancy) AS available_beds FROM hostel h JOIN hostel_room hr ON h.hostel_id = hr.hostel_id WHERE hr.current_occupancy < hr.capacity ORDER BY available_beds DESC;"
        if "floor" in p:
            m = re.search(r"(\d+)(?:st|nd|rd|th)?\s+floor", p)
            flr = m.group(1) if m else "1"
            return f"SELECT h.hostel_name, hr.room_number, hr.capacity, hr.current_occupancy FROM hostel h JOIN hostel_room hr ON h.hostel_id = hr.hostel_id WHERE hr.floor_number = {flr};"
        if "student" in p or "who lives" in p or "resident" in p:
            return "SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, h.hostel_name, hr.room_number, h.warden_name FROM student s JOIN hostel_allocation ha ON s.student_id = ha.student_id JOIN hostel_room hr ON ha.room_id = hr.room_id JOIN hostel h ON hr.hostel_id = h.hostel_id;"
        return "SELECT h.hostel_name, h.gender, h.total_capacity, SUM(hr.current_occupancy) AS total_occupied FROM hostel h JOIN hostel_room hr ON h.hostel_id = hr.hostel_id GROUP BY h.hostel_id, h.hostel_name, h.gender, h.total_capacity;"

    # 12. Placement Queries
    if "placement" in p or "company" in p or "package" in p or "drive" in p or "ctc" in p or "lpa" in p:
        m = re.search(r"(?:package|ctc|lpa|drive)?.*?(>|<|>=|<=|=)\s*(\d+(?:\.\d+)?)", p)
        if m and m.group(2) and float(m.group(2)) > 0:
            return f"SELECT c.company_name, c.tier, pd.package_lpa, pd.min_cgpa, pd.drive_date, pd.venue FROM placement_drive pd JOIN company c ON pd.company_id = c.company_id WHERE pd.package_lpa {m.group(1)} {m.group(2)} ORDER BY pd.package_lpa DESC;"
        if "highest package" in p or "top package" in p:
            return "SELECT c.company_name, c.tier, pd.package_lpa, pd.min_cgpa, pd.drive_date FROM placement_drive pd JOIN company c ON pd.company_id = c.company_id ORDER BY pd.package_lpa DESC LIMIT 5;"
        if "offer" in p or "selected" in p:
            return "SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, c.company_name, pd.package_lpa, pr.status FROM placement_registration pr JOIN student s ON pr.student_id = s.student_id JOIN placement_drive pd ON pr.drive_id = pd.drive_id JOIN company c ON pd.company_id = c.company_id WHERE pr.status = 'Offered' ORDER BY pd.package_lpa DESC;"
        return "SELECT c.company_name, c.tier, pd.package_lpa, pd.min_cgpa, pd.drive_date FROM placement_drive pd JOIN company c ON pd.company_id = c.company_id ORDER BY pd.package_lpa DESC;"

    # 13. Library Queries
    if "library" in p or "book" in p or "author" in p or "isbn" in p:
        if "overdue" in p or "fine" in p or "due" in p or "not returned" in p:
            return "SELECT s.roll_number, s.first_name || ' ' || s.last_name AS student_name, b.title, lt.due_date, (CURRENT_DATE - lt.due_date) AS overdue_days, (CURRENT_DATE - lt.due_date) * 5.00 AS fine_inr FROM library_transaction lt JOIN student s ON lt.student_id = s.student_id JOIN library_book b ON lt.book_id = b.book_id WHERE lt.return_date IS NULL AND lt.due_date < CURRENT_DATE;"
        if "available" in p or "out of stock" in p or "= 0" in p or "zero" in p:
            return "SELECT title, author, isbn, total_copies, available_copies FROM library_book WHERE available_copies = 0;"
        return "SELECT title, author, isbn, total_copies, available_copies FROM library_book ORDER BY title LIMIT 20;"

    # 14. Courses
    if "course" in p or "subject" in p:
        m = re.search(r"credits?\s*(>|<|>=|<=|=)\s*(\d+)", p)
        if m:
            return f"SELECT course_code, course_name, credits, semester_number, course_type FROM course WHERE credits {m.group(1)} {m.group(2)} ORDER BY credits DESC;"
        if "semester" in p:
            m = re.search(r"semester\s*(\d+)", p)
            snum = m.group(1) if m else "1"
            return f"SELECT course_code, course_name, credits, course_type FROM course WHERE semester_number = {snum};"
        return "SELECT course_code, course_name, credits, semester_number, course_type FROM course ORDER BY semester_number, course_code;"

    # 15. Departments
    if "department" in p:
        if "student" in p or "strength" in p or "enrollment" in p:
            return "SELECT d.department_name, COUNT(s.student_id) AS total_students, ROUND(AVG(s.cgpa), 2) AS avg_cgpa FROM department d LEFT JOIN student s ON d.department_id = s.department_id GROUP BY d.department_name ORDER BY total_students DESC;"
        if "faculty" in p or "teachers" in p:
            return "SELECT d.department_name, COUNT(f.faculty_id) AS faculty_count FROM department d LEFT JOIN faculty f ON d.department_id = f.department_id GROUP BY d.department_name ORDER BY faculty_count DESC;"
        return "SELECT department_code, department_name, established_year, contact_email FROM department ORDER BY department_name;"

    # 16. Fallback General Student query
    if "student" in p:
        if "female" in p or "girls" in p or "women" in p:
            return "SELECT roll_number, first_name || ' ' || last_name AS student_name, current_semester, cgpa FROM student WHERE gender = 'Female' AND status = 'Active' ORDER BY cgpa DESC;"
        if "male" in p or "boys" in p or "men" in p:
            return "SELECT roll_number, first_name || ' ' || last_name AS student_name, current_semester, cgpa FROM student WHERE gender = 'Male' AND status = 'Active' ORDER BY cgpa DESC;"
        return "SELECT roll_number, first_name || ' ' || last_name AS student_name, current_year, current_semester, cgpa, status FROM student WHERE status = 'Active' ORDER BY roll_number LIMIT 20;"

    # 17. Default fallback query
    return "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"

@app.route("/api/ai/sql-translate", methods=["POST"])
def ai_sql_translate():
    data = request.get_json() or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return err("Prompt is empty")
    
    # 1. Check if Gemini / Google API Key is set
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    sql = None
    if api_key:
        sql = _call_gemini_api(prompt, api_key)
    
    # 2. Universal Semantic Engine
    if not sql:
        sql = universal_nlp_to_sql(prompt)
        
    return ok(sql=sql, prompt=prompt)

if __name__ == "__main__":
    print("="*55)
    print("  CampusOS  →  http://127.0.0.1:5000")
    print("="*55)
    app.run(debug=True, port=5000, use_reloader=False)


