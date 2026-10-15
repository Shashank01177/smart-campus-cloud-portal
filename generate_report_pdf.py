"""
CampusOS Project Report PDF Generator
Strictly adhering to 23AIE303 DBMS Guidelines and Section Order:
1. Project Title
2. Team Members
3. Introduction and Problem Statement
4. Conceptual and Logical Database Design
5. Normalization and Functional Dependencies
6. Advanced SQL Implementation and Query Design
7. ER Diagram and UML Diagram
8. Relational Schema
9. Database Tables (Structure, Keys, Sample Records)
10. Conclusion and Future Scope
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Don't draw headers/footers on title cover page (page 1)
        if self._pageNumber > 1:
            # Header
            self.drawString(54, 11 * inch - 36, "23AIE303: Database Management Systems — Project Report")
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "CampusOS Digital Twin")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
            
            # Footer
            self.drawString(54, 36, "Amrita Vishwa Vidyapeetham | Dept. of AI & Data Engineering")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(8.5 * inch - 54, 36, page_text)
            self.line(54, 46, 8.5 * inch - 54, 46)
        
        self.restoreState()

def build_pdf(filename="CampusOS_DBMS_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom typography
    c_primary = colors.HexColor("#0f172a")     # Slate 900
    c_accent  = colors.HexColor("#2563eb")     # Blue 600
    c_body    = colors.HexColor("#334155")     # Slate 700
    c_border  = colors.HexColor("#e2e8f0")     # Slate 200
    c_bg_sub  = colors.HexColor("#f8fafc")     # Slate 50
    c_chip_bg = colors.HexColor("#eff6ff")     # Blue 50

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=c_primary,
        alignment=1, # Center
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        alignment=1,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_accent,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_body,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # ═══════════════════════════════════════════════════════════════════════
    # 1. TITLE & COVER HEADER
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 20))
    story.append(Paragraph("AMRITA VISHWA VIDYAPEETHAM", ParagraphStyle('UnivHeader', fontName='Helvetica-Bold', fontSize=12, leading=14, alignment=1, textColor=colors.HexColor("#475569"))))
    story.append(Paragraph("School of Artificial Intelligence & Data Engineering", ParagraphStyle('DeptHeader', fontName='Helvetica', fontSize=10, leading=12, alignment=1, textColor=colors.HexColor("#64748b"))))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=4, spaceAfter=15))

    story.append(Paragraph("CAMPUSOS: SMART CAMPUS DIGITAL TWIN & UNIVERSITY MANAGEMENT SYSTEM", title_style))
    story.append(Paragraph("Course Code: 23AIE303 — Database Management Systems | Final Project Report", subtitle_style))

    # ═══════════════════════════════════════════════════════════════════════
    # 2. TEAM MEMBERS & PROJECT METADATA
    # ═══════════════════════════════════════════════════════════════════════
    meta_table_data = [
        [Paragraph("<b>Author / Student Name:</b>", body_style), Paragraph("Sasank (CB.SC.U4AIE24026)", body_style)],
        [Paragraph("<b>Roll Number:</b>", body_style), Paragraph("CB.SC.U4AIE24026", body_style)],
        [Paragraph("<b>Degree & Program:</b>", body_style), Paragraph("B.Tech in Artificial Intelligence & Data Engineering", body_style)],
        [Paragraph("<b>Course Instructor:</b>", body_style), Paragraph("Faculty of Computer Science & Engineering", body_style)],
        [Paragraph("<b>Live Cloud Deployment URL:</b>", body_style), Paragraph("<u>https://campusos-sasank.azurewebsites.net</u>", body_style)],
        [Paragraph("<b>GitHub Repository URL:</b>", body_style), Paragraph("<u>https://github.com/Shashank01177/smart-campus-cloud-portal</u>", body_style)],
        [Paragraph("<b>Cloud Platform & Database:</b>", body_style), Paragraph("Microsoft Azure App Service | PostgreSQL 18 Flexible Server", body_style)],
        [Paragraph("<b>Submission Date:</b>", body_style), Paragraph("October 2026", body_style)]
    ]
    t_meta = Table(meta_table_data, colWidths=[180, 324])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_sub),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))

    # ═══════════════════════════════════════════════════════════════════════
    # 3. INTRODUCTION AND PROBLEM STATEMENT
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("1. Introduction and Problem Statement", h1_style))
    story.append(Paragraph(
        "<b>1.1 Executive Summary:</b> Modern collegiate ecosystems involve dozens of interconnected operational departments—including academic admissions, course enrollments, attendance accounting, examination evaluations, faculty schedules, physical hostel room allocations, library book loans, and corporate placement drives. In traditional university management setups, these domains operate in isolated silos, causing high data redundancy, concurrency anomalies, inconsistent student records, and lack of real-time visibility.",
        body_style
    ))
    story.append(Paragraph(
        "<b>1.2 Problem Statement:</b> Design, model, implement, and deploy a centralized, production-grade Relational Database Management System (RDBMS) paired with an interactive 3D digital twin interface that provides seamless Role-Based Access Control (RBAC) across Students, Faculty, and Administrators. The system must enforce comprehensive data integrity (Domain, Entity, Referential), eliminate update/deletion anomalies through 3NF/BCNF normalization, execute high-throughput complex SQL analytical queries, and be hosted natively on Microsoft Azure Cloud.",
        body_style
    ))
    story.append(Paragraph(
        "<b>1.3 Key Objectives:</b>", body_style
    ))
    story.append(Paragraph("• <b>Relational Architecture:</b> Model 25 distinct relational entities with strict primary/foreign key hierarchies and cascading integrity constraints.", bullet_style))
    story.append(Paragraph("• <b>Normalization & Normal Forms:</b> Eliminate functional dependency violations to achieve Boyce-Codd Normal Form (BCNF) across all operational schemas.", bullet_style))
    story.append(Paragraph("• <b>Role-Based Security:</b> Implement administrative isolation where sensitive mutation operations (such as student enrollment additions and deletions) are strictly restricted to verified Admin roles, while Faculty and Students maintain appropriate read-only or scoped access.", bullet_style))
    story.append(Paragraph("• <b>Cloud Native Deployment:</b> Host PostgreSQL 18 Flexible Server and Python/Flask backend on Microsoft Azure, containerized via Docker and monitored in real-time through Azure Application Insights.", bullet_style))

    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════
    # 4. CONCEPTUAL AND LOGICAL DATABASE DESIGN
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("2. Conceptual and Logical Database Design", h1_style))
    story.append(Paragraph(
        "The conceptual design translates high-level campus organizational rules into an Entity-Relationship model comprising strong entities, weak entities, and associative entities representing many-to-many relationships. Logical database design maps these entities into normalized relational tables.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Core Functional Domains Modeled:</b>", body_style
    ))
    story.append(Paragraph("1. <b>Academic Core:</b> <code>department</code> (1:N) <code>program</code> (1:N) <code>student</code>; <code>department</code> (1:N) <code>faculty</code>; <code>department</code> (1:N) <code>course</code>.", bullet_style))
    story.append(Paragraph("2. <b>Enrollment & Instruction:</b> <code>student_course_enrollment</code> (M:N between Student and Course) and <code>faculty_course</code> (M:N between Faculty and Course).", bullet_style))
    story.append(Paragraph("3. <b>Academic Tracking:</b> <code>attendance</code> (Daily student tracking per course) and <code>marks</code> linked with <code>examination</code> schemas.", bullet_style))
    story.append(Paragraph("4. <b>Campus Facilities:</b> <code>hostel</code> (1:N) <code>hostel_room</code> (1:1 active) <code>hostel_allocation</code>; <code>library_book</code> (1:N) <code>library_transaction</code>.", bullet_style))
    story.append(Paragraph("5. <b>Career & Administration:</b> <code>company</code> (1:N) <code>placement_drive</code> (1:N) <code>placement_registration</code>; <code>fee</code> ledger; <code>app_user</code> RBAC authentication.", bullet_style))

    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════
    # 5. NORMALIZATION AND FUNCTIONAL DEPENDENCIES
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("3. Normalization and Functional Dependencies", h1_style))
    story.append(Paragraph(
        "To guarantee data consistency, avoid data redundancy, and prevent Insertion, Deletion, and Modification anomalies, the relational schema was rigorously analyzed against Functional Dependencies (FDs) from 1NF through BCNF.",
        body_style
    ))
    
    norm_data = [
        [Paragraph("<b>Normal Form</b>", body_style), Paragraph("<b>Constraint / Condition Enforced</b>", body_style), Paragraph("<b>CampusOS Implementation Example</b>", body_style)],
        [
            Paragraph("<b>1NF</b><br/>(First Normal Form)", body_style),
            Paragraph("Atomic attribute values, unique column names, identification of a primary key.", body_style),
            Paragraph("Multi-valued attributes like course enrollments, student phone numbers, or qualifications were decomposed into distinct atomic columns or normalized associative tables (<code>student_course_enrollment</code>).", body_style)
        ],
        [
            Paragraph("<b>2NF</b><br/>(Second Normal Form)", body_style),
            Paragraph("Must be in 1NF + No partial functional dependencies (all non-prime attributes fully functionally dependent on whole candidate key).", body_style),
            Paragraph("In <code>student_course_enrollment(student_id, course_id)</code>, attributes like <code>course_name</code> or <code>credits</code> were not stored; they reside solely in <code>course</code> referenced by <code>course_id</code>.", body_style)
        ],
        [
            Paragraph("<b>3NF</b><br/>(Third Normal Form)", body_style),
            Paragraph("Must be in 2NF + No transitive dependencies (non-prime attributes must not determine other non-prime attributes; X → Y implies X is superkey or Y is prime).", body_style),
            Paragraph("In <code>student</code>, <code>department_name</code> and <code>hod_id</code> are not stored directly. The table stores foreign key <code>department_id</code>, eliminating transitive dependency: <code>student_id → department_id → department_name</code>.", body_style)
        ],
        [
            Paragraph("<b>BCNF</b><br/>(Boyce-Codd NF)", body_style),
            Paragraph("For every non-trivial functional dependency X → Y, X must be a superkey.", body_style),
            Paragraph("In <code>hostel_room</code>, room numbers are scoped by <code>hostel_id</code>. Primary key is <code>room_id</code>, with candidate key <code>(hostel_id, room_number)</code>. All determinants are candidate keys.", body_style)
        ]
    ]
    t_norm = Table(norm_data, colWidths=[80, 200, 224])
    t_norm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_chip_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_norm)

    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════
    # 6. ADVANCED SQL IMPLEMENTATION AND QUERY DESIGN
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("4. Advanced SQL Implementation and Query Design", h1_style))
    story.append(Paragraph(
        "CampusOS demonstrates advanced SQL techniques utilizing multi-table joins, subqueries, grouping sets, conditional counting, null handling, and aggregated analytics across hundreds of thousands of production records.",
        body_style
    ))

    story.append(Paragraph("<b>4.1 Complex Analytical Query 1: Comprehensive Student Academic & Attendance Analytics</b>", h2_style))
    story.append(Paragraph("<i>Purpose:</i> Aggregates student demographic info, department, enrolled courses count, grade average, total lectures conducted, lectures attended, and calculated attendance percentage.", body_style))
    
    q1_text = """SELECT 
    s.roll_number,
    s.first_name || ' ' || s.last_name AS student_name,
    d.department_name,
    s.cgpa,
    COUNT(DISTINCT sce.course_id) AS enrolled_courses,
    ROUND(AVG(m.marks_obtained), 2) AS avg_marks,
    COUNT(a.attendance_id) AS total_sessions,
    ROUND((COUNT(CASE WHEN a.status = 'Present' THEN 1 END)::numeric / 
           NULLIF(COUNT(a.attendance_id), 0)) * 100, 2) AS attendance_pct
FROM student s
JOIN department d ON s.department_id = d.department_id
LEFT JOIN student_course_enrollment sce ON s.student_id = sce.student_id
LEFT JOIN marks m ON s.student_id = m.student_id
LEFT JOIN attendance a ON s.student_id = a.student_id
WHERE s.status = 'Active'
GROUP BY s.student_id, s.roll_number, s.first_name, s.last_name, d.department_name, s.cgpa
ORDER BY s.cgpa DESC LIMIT 10;"""

    t_q1 = Table([[Paragraph(q1_text.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)]], colWidths=[504])
    t_q1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_q1)

    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.2 Complex Analytical Query 2: Hostel Bed Capacity & Real-Time Vacancy Ledger</b>", h2_style))
    story.append(Paragraph("<i>Purpose:</i> Calculates total block rooms, aggregate bed capacity, current occupied beds, and remaining vacancy per hostel block.", body_style))
    
    q2_text = """SELECT 
    h.hostel_name,
    h.gender,
    COUNT(hr.room_id) AS total_rooms,
    SUM(hr.capacity) AS total_bed_capacity,
    COUNT(ha.allocation_id) AS occupied_beds,
    (SUM(hr.capacity) - COUNT(ha.allocation_id)) AS vacant_beds,
    ROUND((COUNT(ha.allocation_id)::numeric / NULLIF(SUM(hr.capacity), 0)) * 100, 2) AS occupancy_rate
FROM hostel h
JOIN hostel_room hr ON h.hostel_id = hr.hostel_id
LEFT JOIN hostel_allocation ha ON hr.room_id = ha.room_id AND ha.vacation_date IS NULL
GROUP BY h.hostel_id, h.hostel_name, h.gender
ORDER BY occupancy_rate DESC;"""

    t_q2 = Table([[Paragraph(q2_text.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)]], colWidths=[504])
    t_q2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_q2)

    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════
    # 7. ER DIAGRAM AND UML DIAGRAM
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("5. ER Diagram and UML Diagram", h1_style))
    story.append(Paragraph(
        "<b>5.1 Entity-Relationship (ER) Architecture:</b> The diagram illustrates cardinalities, participation constraints, and foreign key relationships across major campus entities.",
        body_style
    ))
    
    er_ascii = """+------------------+         1:N          +-------------------+        1:N         +-------------------+
|    DEPARTMENT    | -------------------> |      FACULTY      | -----------------> |   FACULTY_COURSE  |
+------------------+                      +-------------------+                    +-------------------+
        | 1:N                                                                                | M:N
        v                                                                                    v
+------------------+         1:N          +-------------------+        M:N         +-------------------+
|     PROGRAM      | -------------------> |      STUDENT      | <================> |      COURSE       |
+------------------+                      +-------------------+  (enrollment)      +-------------------+
                                            |   |   |   |                                    | 1:N
                  +-------------------------+   |   |   +-------------------+                v
                  | 1:N                         |   | 1:N                   | 1:1      +-------------------+
                  v                             |   v                       v          |    EXAMINATION    |
        +-------------------+                   | +---------------+   +--------------+ +-------------------+
        |    ATTENDANCE     |                   | |  HOSTEL_ALLOC |   |   APP_USER   |           | 1:N
        +-------------------+                   | +---------------+   |    (RBAC)    |           v
                                                v         |           +--------------+ +-------------------+
                                        +-------------+   v 1:1                        |       MARKS       |
                                        |     FEE     | +-------------+                +-------------------+
                                        +-------------+ | HOSTEL_ROOM |
                                                        +-------------+"""

    t_er = Table([[Paragraph(er_ascii.replace("\n", "<br/>").replace(" ", "&nbsp;"), ParagraphStyle('ER', fontName='Courier', fontSize=6.5, leading=8.5, textColor=colors.HexColor("#1e293b")))]], colWidths=[504])
    t_er.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_er)

    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════
    # 8. RELATIONAL SCHEMA
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("6. Relational Schema Mapping", h1_style))
    story.append(Paragraph(
        "Below is the relational mapping of tables with primary keys (<u>underlined</u>) and foreign keys (<i>italicized with FK marker</i>):",
        body_style
    ))
    
    schema_items = [
        "<b>DEPARTMENT</b> (<u>department_id</u>, department_name, department_code, <i>hod_id [FK]</i>, established_year, contact_email)",
        "<b>PROGRAM</b> (<u>program_id</u>, <i>department_id [FK]</i>, program_name, degree_level, duration_years, total_semesters)",
        "<b>FACULTY</b> (<u>faculty_id</u>, <i>department_id [FK]</i>, first_name, last_name, email, phone, designation, joining_date, salary)",
        "<b>STUDENT</b> (<u>student_id</u>, roll_number, first_name, last_name, email, phone, gender, dob, <i>department_id [FK]</i>, <i>program_id [FK]</i>, admission_year, current_year, current_semester, cgpa, status)",
        "<b>COURSE</b> (<u>course_id</u>, course_code, course_name, <i>department_id [FK]</i>, <i>program_id [FK]</i>, credits, semester_number, course_type)",
        "<b>FACULTY_COURSE</b> (<u>allocation_id</u>, <i>faculty_id [FK]</i>, <i>course_id [FK]</i>, academic_year, semester_type)",
        "<b>STUDENT_COURSE_ENROLLMENT</b> (<u>enrollment_id</u>, <i>student_id [FK]</i>, <i>course_id [FK]</i>, enrollment_date, status)",
        "<b>ATTENDANCE</b> (<u>attendance_id</u>, <i>student_id [FK]</i>, <i>course_id [FK]</i>, date, status, <i>marked_by [FK]</i>)",
        "<b>EXAMINATION</b> (<u>exam_id</u>, <i>course_id [FK]</i>, exam_type, exam_date, max_marks, weightage_percent)",
        "<b>MARKS</b> (<u>mark_id</u>, <i>student_id [FK]</i>, <i>exam_id [FK]</i>, marks_obtained, grade)",
        "<b>FEE</b> (<u>fee_id</u>, <i>student_id [FK]</i>, fee_type, amount, due_date, payment_status, paid_date)",
        "<b>HOSTEL</b> (<u>hostel_id</u>, hostel_name, gender, total_capacity, warden_name, warden_phone)",
        "<b>HOSTEL_ROOM</b> (<u>room_id</u>, <i>hostel_id [FK]</i>, room_number, capacity, current_occupancy, floor_number)",
        "<b>HOSTEL_ALLOCATION</b> (<u>allocation_id</u>, <i>student_id [FK]</i>, <i>room_id [FK]</i>, allocation_date, vacation_date)",
        "<b>LIBRARY_BOOK</b> (<u>book_id</u>, isbn, title, author, <i>department_id [FK]</i>, total_copies, available_copies)",
        "<b>LIBRARY_TRANSACTION</b> (<u>transaction_id</u>, <i>book_id [FK]</i>, <i>student_id [FK]</i>, issue_date, due_date, return_date, fine_amount)",
        "<b>COMPANY</b> (<u>company_id</u>, company_name, industry_type, contact_email, tier)",
        "<b>PLACEMENT_DRIVE</b> (<u>drive_id</u>, <i>company_id [FK]</i>, drive_date, package_lpa, min_cgpa, venue)",
        "<b>PLACEMENT_REGISTRATION</b> (<u>registration_id</u>, <i>drive_id [FK]</i>, <i>student_id [FK]</i>, status)",
        "<b>APP_USER</b> (<u>user_id</u>, email, password_hash, plain_password, role, linked_id, full_name, created_at)"
    ]
    for s_item in schema_items:
        story.append(Paragraph(f"• {s_item}", ParagraphStyle('SchemaItem', parent=body_style, fontSize=8, leading=11, spaceAfter=2)))

    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════
    # 9. DATABASE TABLES
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("7. Database Tables, Attributes, Constraints & Sample Data", h1_style))
    story.append(Paragraph(
        "Below are detailed structural specifications for primary operational tables verified live in the Azure PostgreSQL instance (Total Student Count: 1,938; Courses: 330; Faculty: 73; Books: 200).",
        body_style
    ))

    # Table 1: STUDENT
    story.append(Paragraph("<b>Table 7.1: student (Entity Table)</b>", h2_style))
    student_cols = [
        [Paragraph("<b>Attribute Name</b>", body_style), Paragraph("<b>Data Type</b>", body_style), Paragraph("<b>Constraint / Key</b>", body_style), Paragraph("<b>Sample Record Value</b>", body_style)],
        [Paragraph("student_id", code_style), Paragraph("INTEGER", code_style), Paragraph("PRIMARY KEY (AUTO_INC)", body_style), Paragraph("1", body_style)],
        [Paragraph("roll_number", code_style), Paragraph("VARCHAR(30)", code_style), Paragraph("UNIQUE, NOT NULL", body_style), Paragraph("CB.SC.U4AIE24026", body_style)],
        [Paragraph("first_name", code_style), Paragraph("VARCHAR(50)", code_style), Paragraph("NOT NULL", body_style), Paragraph("Sasank", body_style)],
        [Paragraph("last_name", code_style), Paragraph("VARCHAR(50)", code_style), Paragraph("NOT NULL", body_style), Paragraph("Reddy", body_style)],
        [Paragraph("email", code_style), Paragraph("VARCHAR(100)", code_style), Paragraph("UNIQUE, NOT NULL", body_style), Paragraph("cb.sc.u4aie24026@cb.students.amrita.edu", body_style)],
        [Paragraph("gender", code_style), Paragraph("VARCHAR(10)", code_style), Paragraph("CHECK (gender IN ('Male','Female','Other'))", body_style), Paragraph("Male", body_style)],
        [Paragraph("department_id", code_style), Paragraph("INTEGER", code_style), Paragraph("FOREIGN KEY (department) ON DELETE RESTRICT", body_style), Paragraph("2 (AI & Data Engineering)", body_style)],
        [Paragraph("current_year", code_style), Paragraph("INTEGER", code_style), Paragraph("CHECK (current_year BETWEEN 1 AND 5)", body_style), Paragraph("2", body_style)],
        [Paragraph("cgpa", code_style), Paragraph("NUMERIC(4,2)", code_style), Paragraph("CHECK (cgpa BETWEEN 0.00 AND 10.00)", body_style), Paragraph("8.75", body_style)],
        [Paragraph("status", code_style), Paragraph("VARCHAR(20)", code_style), Paragraph("DEFAULT 'Active'", body_style), Paragraph("Active", body_style)]
    ]
    t_stud = Table(student_cols, colWidths=[100, 80, 184, 140])
    t_stud.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_bg_sub),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_stud)

    story.append(Spacer(1, 8))

    # Table 2: COURSE
    story.append(Paragraph("<b>Table 7.2: course (Academic Entity)</b>", h2_style))
    course_cols = [
        [Paragraph("<b>Attribute Name</b>", body_style), Paragraph("<b>Data Type</b>", body_style), Paragraph("<b>Constraint / Key</b>", body_style), Paragraph("<b>Sample Record Value</b>", body_style)],
        [Paragraph("course_id", code_style), Paragraph("INTEGER", code_style), Paragraph("PRIMARY KEY (AUTO_INC)", body_style), Paragraph("364", body_style)],
        [Paragraph("course_code", code_style), Paragraph("VARCHAR(20)", code_style), Paragraph("UNIQUE, NOT NULL", body_style), Paragraph("22AIE303", body_style)],
        [Paragraph("course_name", code_style), Paragraph("VARCHAR(150)", code_style), Paragraph("NOT NULL", body_style), Paragraph("Database Management Systems", body_style)],
        [Paragraph("credits", code_style), Paragraph("INTEGER", code_style), Paragraph("CHECK (credits BETWEEN 1 AND 10)", body_style), Paragraph("4", body_style)],
        [Paragraph("department_id", code_style), Paragraph("INTEGER", code_style), Paragraph("FOREIGN KEY (department) ON DELETE SET NULL", body_style), Paragraph("2", body_style)],
        [Paragraph("course_type", code_style), Paragraph("VARCHAR(30)", code_style), Paragraph("CHECK (course_type IN ('Core','Elective','Lab','Project'))", body_style), Paragraph("Core", body_style)]
    ]
    t_crs = Table(course_cols, colWidths=[100, 80, 184, 140])
    t_crs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_bg_sub),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_crs)

    story.append(Spacer(1, 8))

    # Table 3: APP_USER (RBAC)
    story.append(Paragraph("<b>Table 7.3: app_user (Security & Role-Based Access Control)</b>", h2_style))
    user_cols = [
        [Paragraph("<b>Attribute Name</b>", body_style), Paragraph("<b>Data Type</b>", body_style), Paragraph("<b>Constraint / Key</b>", body_style), Paragraph("<b>Sample Record Value</b>", body_style)],
        [Paragraph("user_id", code_style), Paragraph("INTEGER", code_style), Paragraph("PRIMARY KEY (AUTO_INC)", body_style), Paragraph("101", body_style)],
        [Paragraph("email", code_style), Paragraph("VARCHAR(100)", code_style), Paragraph("UNIQUE, NOT NULL", body_style), Paragraph("admin@campusos.edu", body_style)],
        [Paragraph("password_hash", code_style), Paragraph("VARCHAR(255)", code_style), Paragraph("NOT NULL (pbkdf2:sha256)", body_style), Paragraph("pbkdf2:sha256:10000$...", body_style)],
        [Paragraph("role", code_style), Paragraph("VARCHAR(20)", code_style), Paragraph("CHECK (role IN ('Admin','Faculty','Student'))", body_style), Paragraph("Admin", body_style)],
        [Paragraph("linked_id", code_style), Paragraph("INTEGER", code_style), Paragraph("REFERENCES student / faculty id", body_style), Paragraph("NULL (System Admin)", body_style)]
    ]
    t_usr = Table(user_cols, colWidths=[100, 80, 184, 140])
    t_usr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_bg_sub),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_usr)

    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════
    # 10. CONCLUSION AND FUTURE SCOPE
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("8. Conclusion and Future Scope", h1_style))
    story.append(Paragraph(
        "<b>8.1 Conclusion:</b> The CampusOS Smart University Digital Twin successfully demonstrates an end-to-end cloud-native enterprise database system. Built on PostgreSQL 18 and Microsoft Azure, the platform bridges mathematical relational theory with real-world high-throughput university operations. Strict Boyce-Codd Normal Form (BCNF) normalization eliminated anomalies, while cascading foreign keys, check constraints, and role-based authorization protect institutional data integrity. The integration of containerization with Docker, live telemetry with Azure Application Insights, and an interactive 3D frontend delivers an intuitive, secure, and production-ready solution.",
        body_style
    ))
    story.append(Paragraph(
        "<b>8.2 Future Scope & Extensions:</b>", body_style
    ))
    story.append(Paragraph("• <b>Automated Attendance via Edge Vision:</b> Integration with campus camera feeds to log attendance records directly into PostgreSQL using real-time edge facial recognition.", bullet_style))
    story.append(Paragraph("• <b>AI-Powered Predictive Academic Warning:</b> Implementing regression models to identify students with declining attendance and marks trends, automatically flagging them for faculty mentoring.", bullet_style))
    story.append(Paragraph("• <b>Kubernetes Microservices (AKS):</b> Transitioning from monolithic container deployment to microservices orchestrated on Azure Kubernetes Service (AKS) with automated horizontal pod autoscaling.", bullet_style))
    story.append(Paragraph("• <b>Read Replicas & Connection Pooling:</b> Configuring Azure PostgreSQL PgBouncer connection pooling and read replicas across geographical regions to support hundreds of thousands of concurrent portal users during semester result announcements.", bullet_style))

    # Build the PDF document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report successfully generated at: {filename}")

if __name__ == "__main__":
    out_pdf = r"C:\Users\Public\CampusOS_Interactive_Campus_Final\campusos_v4\CampusOS_DBMS_Project_Report.pdf"
    build_pdf(out_pdf)
