import matplotlib.pyplot as plt
import matplotlib.patches as patches

# -------------------------------------------------------------
# 1. CLEAN HIGH-PRECISION ER DIAGRAM
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
ax.set_facecolor('#ffffff')
fig.patch.set_facecolor('#ffffff')

# Grid layout: 4 columns x 3 rows
# Col 0: x=0.6, Col 1: x=4.3, Col 2: x=8.0, Col 3: x=11.7
# Row 0 (Top): y=7.2, Row 1 (Mid): y=4.4, Row 2 (Bot): y=1.5
w = 2.8
h = 1.9

entities = [
    # Top Row
    {"name": "DEPARTMENT", "x": 0.6, "y": 7.3, "color": "#1e3a8a", 
     "cols": ["PK department_id : INT", "   department_name : VARCHAR(100)", "   department_code : VARCHAR(20)", "   established_year : INT"]},
    {"name": "FACULTY", "x": 4.3, "y": 7.3, "color": "#1e3a8a", 
     "cols": ["PK faculty_id : INT", "FK department_id : INT", "   first_name, last_name : VARCHAR", "   designation, salary : NUMERIC"]},
    {"name": "COURSE", "x": 8.0, "y": 7.3, "color": "#b45309", 
     "cols": ["PK course_id : INT", "   course_code : VARCHAR(20)", "   course_name : VARCHAR(150)", "FK department_id : INT", "   credits : INT, type : VARCHAR"]},
    {"name": "HOSTEL", "x": 11.7, "y": 7.3, "color": "#6d28d9", 
     "cols": ["PK hostel_id : INT", "   hostel_name : VARCHAR(100)", "   gender : VARCHAR(10)", "   total_capacity : INT"]},

    # Middle Row
    {"name": "PROGRAM", "x": 0.6, "y": 4.4, "color": "#1e3a8a", 
     "cols": ["PK program_id : INT", "FK department_id : INT", "   program_name : VARCHAR(100)", "   duration_years : INT"]},
    {"name": "STUDENT", "x": 4.3, "y": 4.2, "color": "#047857", 
     "cols": ["PK student_id : INT", "   roll_number : VARCHAR(30) (UQ)", "   first_name, last_name : VARCHAR", "FK department_id, program_id : INT", "   cgpa : NUMERIC(4,2), status : VARCHAR"]},
    {"name": "STUDENT_ENROLLMENT", "x": 8.0, "y": 4.4, "color": "#334155", 
     "cols": ["PK enrollment_id : INT", "FK student_id : INT", "FK course_id : INT", "   enrollment_date : DATE", "   status : VARCHAR(20)"]},
    {"name": "HOSTEL_ROOM & ALLOC", "x": 11.7, "y": 4.4, "color": "#6d28d9", 
     "cols": ["PK room_id, allocation_id : INT", "FK hostel_id : INT", "FK student_id : INT", "   room_number, capacity : INT", "   allocation_date : DATE"]},

    # Bottom Row
    {"name": "ATTENDANCE", "x": 0.6, "y": 1.5, "color": "#334155", 
     "cols": ["PK attendance_id : BIGINT", "FK student_id : INT", "FK course_id : INT", "   date : DATE, status : VARCHAR", "FK marked_by (faculty_id) : INT"]},
    {"name": "MARKS", "x": 4.3, "y": 1.5, "color": "#334155", 
     "cols": ["PK mark_id : BIGINT", "FK student_id : INT", "FK exam_id : INT", "   marks_obtained : NUMERIC(5,2)", "   grade : VARCHAR(5)"]},
    {"name": "EXAMINATION", "x": 8.0, "y": 1.5, "color": "#b45309", 
     "cols": ["PK exam_id : INT", "FK course_id : INT", "   exam_type : VARCHAR(30)", "   max_marks, exam_date", "   weightage_percent : NUMERIC"]},
    {"name": "APP_USER (RBAC)", "x": 11.7, "y": 1.5, "color": "#be123c", 
     "cols": ["PK user_id : INT", "   email : VARCHAR(100) (UQ)", "   password_hash : VARCHAR(255)", "   role : 'Admin'|'Faculty'|'Student'", "FK linked_id : INT"]}
]

for e in entities:
    cur_h = 2.1 if e["name"] == "STUDENT" else h
    # Header
    hdr = patches.FancyBboxPatch((e["x"], e["y"]+cur_h-0.38), w, 0.38, boxstyle="round,pad=0,rounding_size=0.06",
                                 facecolor=e["color"], edgecolor=e["color"], linewidth=1.5)
    ax.add_patch(hdr)
    ax.text(e["x"]+w/2, e["y"]+cur_h-0.19, e["name"], color='white', weight='bold',
            fontsize=8.5, ha='center', va='center')
    
    # Body
    body = patches.FancyBboxPatch((e["x"], e["y"]), w, cur_h-0.38, boxstyle="round,pad=0,rounding_size=0.06",
                                  facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1)
    ax.add_patch(body)
    
    # Attributes
    for idx, col in enumerate(e["cols"]):
        col_clean = col.strip()
        weight = 'bold' if col_clean.startswith("PK") else 'normal'
        color = '#0f172a' if col_clean.startswith("PK") else ('#1d4ed8' if col_clean.startswith("FK") else '#475569')
        ax.text(e["x"]+0.12, e["y"]+cur_h-0.62 - idx*0.27, col, fontsize=7.2, color=color, weight=weight, va='center')

# Orthogonal & clean connectors
lines = [
    # Dept -> Program (Vertical)
    ((2.0, 7.3), (2.0, 6.3), "1:N"),
    # Dept -> Faculty (Horizontal)
    ((3.4, 8.2), (4.3, 8.2), "1:N"),
    # Dept -> Course (Horizontal)
    ((7.1, 8.2), (8.0, 8.2), "1:N"),
    # Program -> Student (Horizontal)
    ((3.4, 5.3), (4.3, 5.3), "1:N"),
    # Student -> Enrollment (Horizontal)
    ((7.1, 5.3), (8.0, 5.3), "1:N"),
    # Course -> Enrollment (Vertical)
    ((9.4, 7.3), (9.4, 6.3), "1:N"),
    # Course -> Exam (Vertical)
    ((9.4, 4.4), (9.4, 3.4), "1:N"),
    # Exam -> Marks (Horizontal)
    ((8.0, 2.4), (7.1, 2.4), "1:N"),
    # Student -> Marks (Vertical)
    ((5.7, 4.2), (5.7, 3.4), "1:N"),
    # Student -> Attendance (Angled/Direct)
    ((4.3, 4.4), (3.4, 3.0), "1:N"),
    # Hostel -> Room (Vertical)
    ((13.1, 7.3), (13.1, 6.3), "1:N"),
    # Student -> Hostel (Horizontal)
    ((7.1, 5.0), (11.7, 5.0), "1:1"),
    # User -> Student/Fac (Horizontal)
    ((11.7, 2.4), (7.1, 2.0), "1:1")
]

for start, end, label in lines:
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2, shrinkA=2, shrinkB=2))
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2
    ax.text(mid_x, mid_y, label, fontsize=6.5, color='#dc2626', weight='bold',
            bbox=dict(boxstyle="square,pad=0.1", facecolor='white', edgecolor='#e2e8f0', alpha=0.9))

ax.set_xlim(0, 15.2)
ax.set_ylim(0.8, 10.0)
ax.axis('off')
plt.title("CampusOS Database Management System — Comprehensive Entity-Relationship (ER) Diagram", fontsize=13, weight='bold', pad=18, color='#0f172a')
plt.tight_layout()
plt.savefig("C:/Users/Public/CampusOS_Interactive_Campus_Final/campusos_v4/er_diagram.png", dpi=300)
plt.close()
print("Clean ER Diagram created successfully!")

# -------------------------------------------------------------
# 2. CLEAN HIGH-PRECISION UML SYSTEM ARCHITECTURE DIAGRAM
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(15, 8), dpi=300)
ax.set_facecolor('#ffffff')
fig.patch.set_facecolor('#ffffff')

uml_layers = [
    {
        "title": "CLIENT PRESENTATION LAYER",
        "sub": "Interactive SPA & 3D Campus Digital Twin",
        "x": 0.6, "y": 1.2, "w": 3.2, "h": 5.8, "color": "#0369a1",
        "items": [
            "HTML5 Isometric Canvas View",
            "Modern Responsive CSS3 Grid",
            "Vanilla JavaScript Core Engine",
            "Role-Based Navigation Portals:",
            "  • Student Workspace",
            "  • Faculty Workspace",
            "  • System Admin Workspace",
            "Dynamic SQL Query Sandbox"
        ]
    },
    {
        "title": "APPLICATION & BUSINESS LAYER",
        "sub": "Microsoft Azure App Service (Linux F1)",
        "x": 4.6, "y": 1.2, "w": 4.5, "h": 5.8, "color": "#1d4ed8",
        "items": [
            "Python 3.11 Execution Environment",
            "Gunicorn WSGI Multi-Worker Server",
            "Flask Application & RESTful API Routing",
            "Session-Based RBAC Auth Middleware",
            "Mutation Guard (Admin Student Security)",
            "Parameterized Query Safety (Psycopg2)",
            "Integrated App Insights SDK Telemetry",
            "Containerized Deployment (Docker)"
        ]
    },
    {
        "title": "DATA PERSISTENCE LAYER",
        "sub": "Azure PostgreSQL Flexible Server",
        "x": 9.9, "y": 4.3, "w": 4.5, "h": 2.7, "color": "#047857",
        "items": [
            "PostgreSQL 18 Database Engine",
            "25 Fully Normalized Relational Tables (BCNF)",
            "1,938 Active Student Records & 330 Courses",
            "Cascading Foreign Keys & Integrity Constraints",
            "ACID Compliant Transaction Engine"
        ]
    },
    {
        "title": "CLOUD MONITORING & DEVOPS",
        "sub": "Azure Container Registry & App Insights",
        "x": 9.9, "y": 1.2, "w": 4.5, "h": 2.7, "color": "#7c2d12",
        "items": [
            "Azure Application Insights Telemetry",
            "Real-Time Request Rates & Latency Tracking",
            "Azure Container Registry (campusosacr24026)",
            "Docker Multi-Stage Container Image",
            "GitHub Actions CI/CD Automation Pipeline"
        ]
    }
]

for l in uml_layers:
    # Header Banner
    hdr = patches.FancyBboxPatch((l["x"], l["y"]+l["h"]-0.85), l["w"], 0.85, boxstyle="round,pad=0,rounding_size=0.08",
                                 facecolor=l["color"], edgecolor=l["color"])
    ax.add_patch(hdr)
    ax.text(l["x"]+l["w"]/2, l["y"]+l["h"]-0.32, l["title"], color='white', weight='bold',
            fontsize=8.5, ha='center', va='center')
    ax.text(l["x"]+l["w"]/2, l["y"]+l["h"]-0.62, l["sub"], color='#93c5fd', style='italic',
            fontsize=7.0, ha='center', va='center')
    
    # Body Box
    body = patches.FancyBboxPatch((l["x"], l["y"]), l["w"], l["h"]-0.85, boxstyle="round,pad=0,rounding_size=0.08",
                                  facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.2)
    ax.add_patch(body)
    
    # Items
    for idx, itm in enumerate(l["items"]):
        indent = 0.35 if itm.startswith("  •") else 0.15
        color = '#0284c7' if itm.startswith("  •") else '#1e293b'
        weight = 'bold' if itm.endswith(":") else 'normal'
        ax.text(l["x"]+indent, l["y"]+l["h"]-1.15 - idx*0.36, itm, fontsize=7.5, color=color, weight=weight, va='center')

# Arrows
ax.annotate("", xy=(4.6, 4.3), xytext=(3.8, 4.3), arrowprops=dict(arrowstyle="<->", color="#0284c7", lw=1.8))
ax.text(4.2, 4.45, "HTTPS / JSON\nREST Endpoints", fontsize=7.2, color='#0369a1', weight='bold', ha='center')

ax.annotate("", xy=(9.9, 5.5), xytext=(9.1, 5.5), arrowprops=dict(arrowstyle="<->", color="#059669", lw=1.8))
ax.text(9.5, 5.65, "TCP 5432 (SSL)\nSQL Queries", fontsize=7.2, color='#047857', weight='bold', ha='center')

ax.annotate("", xy=(9.9, 2.5), xytext=(9.1, 2.5), arrowprops=dict(arrowstyle="->", color="#b45309", lw=1.8))
ax.text(9.5, 2.65, "Telemetry & Logs\n(Live Diagnostics)", fontsize=7.2, color='#7c2d12', weight='bold', ha='center')

ax.set_xlim(0, 15.0)
ax.set_ylim(0.5, 7.8)
ax.axis('off')
plt.title("CampusOS Enterprise System Architecture & Deployment UML Diagram", fontsize=13, weight='bold', pad=18, color='#0f172a')
plt.tight_layout()
plt.savefig("C:/Users/Public/CampusOS_Interactive_Campus_Final/campusos_v4/uml_diagram.png", dpi=300)
plt.close()
print("Clean UML Diagram created successfully!")
