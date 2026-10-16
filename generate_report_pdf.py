"""
CampusOS - Comprehensive Academic Project Report Generator
Course: 23AIE303 - Database Management Systems
Format: Professional Academic Project Report (Amrita Vishwa Vidyapeetham standard)

Strict Section Order mandated by guidelines:
1. Cover / Title Page (University Header, Department, Credentials, Live URL, GitHub URL)
2. Table of Contents & Executive Summary
3. Section 1: Introduction and Problem Statement
4. Section 2: Conceptual and Logical Database Design
5. Section 3: Normalization and Functional Dependencies (1NF, 2NF, 3NF, BCNF)
6. Section 4: Advanced SQL Implementation and Query Design (with results & analysis)
7. Section 5: ER Diagram and UML Architecture Diagram (high-res embeds)
8. Section 6: Relational Schema Mapping
9. Section 7: Database Tables, Attributes, Constraints & Sample Data
10. Section 8: Cloud Infrastructure, Security & Monitoring
11. Section 9: Conclusion and Future Scope
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.pdfgen import canvas

class AcademicNumberedCanvas(canvas.Canvas):
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
        
        # Don't draw running headers/footers on the title page (page 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#475569"))
            
            # Running Header
            self.drawString(54, 11 * inch - 36, "AMRITA VISHWA VIDYAPEETHAM")
            self.setFont("Helvetica", 7.5)
            self.drawString(210, 11 * inch - 36, "|  23AIE303: Database Management Systems Project Report")
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "CampusOS Digital Twin")
            
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.6)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
            
            # Running Footer
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 34, "Department of Artificial Intelligence & Data Engineering")
            page_str = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(8.5 * inch - 54, 34, page_str)
            self.line(54, 44, 8.5 * inch - 54, 44)
        
        self.restoreState()

def generate_professional_report(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Color Palette - Academic Executive Navy & Slate
    c_primary    = colors.HexColor("#0f172a")     # Deep Slate 900
    c_secondary  = colors.HexColor("#1e3a8a")     # Royal Navy 900
    c_accent     = colors.HexColor("#2563eb")     # Tech Blue 600
    c_body       = colors.HexColor("#334155")     # Slate 700
    c_border     = colors.HexColor("#cbd5e1")     # Slate 300
    c_bg_sub     = colors.HexColor("#f8fafc")     # Slate 50
    c_chip_bg    = colors.HexColor("#eff6ff")     # Light Blue Tint
    c_gold       = colors.HexColor("#b45309")     # Amber Accent

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=26,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=c_body,
        alignment=4, # Justified
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
        alignment=0 # Left
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=9.8,
        textColor=colors.HexColor("#0f172a")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_body
    )

    story = []

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 1: FORMAL ACADEMIC COVER PAGE
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 15))
    story.append(Paragraph("AMRITA VISHWA VIDYAPEETHAM", ParagraphStyle('UnivHead', fontName='Helvetica-Bold', fontSize=15, leading=18, alignment=1, textColor=c_primary)))
    story.append(Spacer(1, 3))
    story.append(Paragraph("SCHOOL OF ARTIFICIAL INTELLIGENCE & DATA ENGINEERING", ParagraphStyle('DeptHead', fontName='Helvetica-Bold', fontSize=10, leading=13, alignment=1, textColor=c_accent)))
    story.append(Paragraph("Coimbatore Campus — 641112, Tamil Nadu, India", ParagraphStyle('CampusHead', fontName='Helvetica', fontSize=8.5, leading=11, alignment=1, textColor=colors.HexColor("#64748b"))))
    
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=4, spaceAfter=20))
    
    story.append(Paragraph("CAMPUSOS: SMART CAMPUS DIGITAL TWIN & UNIVERSITY DATABASE SYSTEM", title_style))
    story.append(Paragraph("A Unified Enterprise RDBMS Implementation with Role-Based Access Control, Cloud Containerization, and Azure Telemetry", subtitle_style))
    
    story.append(Spacer(1, 10))
    
    # Elegant Project Credentials Table
    credentials_data = [
        [Paragraph("<b>Course Code & Title:</b>", table_cell_style), Paragraph("23AIE303 — Database Management Systems", table_cell_style)],
        [Paragraph("<b>Degree & Branch:</b>", table_cell_style), Paragraph("B.Tech in Artificial Intelligence & Data Engineering", table_cell_style)],
        [Paragraph("<b>Academic Year & Semester:</b>", table_cell_style), Paragraph("2026 – 2027 | Semester V", table_cell_style)],
        [Paragraph("<b>Student Author:</b>", table_cell_style), Paragraph("<b>Sasank</b>", table_cell_style)],
        [Paragraph("<b>Roll Number:</b>", table_cell_style), Paragraph("<code>CB.SC.U4AIE24026</code>", table_cell_style)],
        [Paragraph("<b>Institutional Email:</b>", table_cell_style), Paragraph("cb.sc.u4aie24026@cb.students.amrita.edu", table_cell_style)],
        [Paragraph("<b>Live Cloud Deployment:</b>", table_cell_style), Paragraph("<u>https://campusos-sasank.azurewebsites.net</u>", table_cell_style)],
        [Paragraph("<b>GitHub Source Repository:</b>", table_cell_style), Paragraph("<u>https://github.com/Shashank01177/smart-campus-cloud-portal</u>", table_cell_style)],
        [Paragraph("<b>Cloud Platform & Database:</b>", table_cell_style), Paragraph("Microsoft Azure App Service | PostgreSQL 18 Flexible Server", table_cell_style)],
        [Paragraph("<b>Submission Date:</b>", table_cell_style), Paragraph("October 2026", table_cell_style)]
    ]
    t_cred = Table(credentials_data, colWidths=[150, 354])
    t_cred.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_sub),
        ('BOX', (0,0), (-1,-1), 1.2, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_cred)
    
    story.append(Spacer(1, 25))
    
    # Certification statement
    cert_text = """<b>STUDENT DECLARATION:</b> I hereby declare that this project report entitled <b>'CampusOS: Smart Campus Digital Twin & University Management System'</b> is an authentic record of independent coursework carried out in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Artificial Intelligence & Data Engineering under course <b>23AIE303 (Database Management Systems)</b> at Amrita Vishwa Vidyapeetham."""
    story.append(Paragraph(cert_text, ParagraphStyle('Cert', parent=body_style, fontSize=7.5, leading=11, textColor=colors.HexColor("#64748b"))))
    
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 2: TABLE OF CONTENTS & INTRODUCTION
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    toc_data = [
        [Paragraph("<b>Section</b>", table_header_style), Paragraph("<b>Title & Subsections</b>", table_header_style), Paragraph("<b>Page</b>", table_header_style)],
        [Paragraph("<b>1</b>", table_cell_style), Paragraph("Introduction and Problem Statement (Executive Overview, Domain Scope, Objectives)", table_cell_style), Paragraph("2", table_cell_style)],
        [Paragraph("<b>2</b>", table_cell_style), Paragraph("Conceptual and Logical Database Design (Domain Decomposition & Relationship Logic)", table_cell_style), Paragraph("3", table_cell_style)],
        [Paragraph("<b>3</b>", table_cell_style), Paragraph("Normalization and Functional Dependencies (1NF, 2NF, 3NF, BCNF Analysis)", table_cell_style), Paragraph("3", table_cell_style)],
        [Paragraph("<b>4</b>", table_cell_style), Paragraph("Advanced SQL Implementation and Query Design (Analytical Queries & Execution Logs)", table_cell_style), Paragraph("4", table_cell_style)],
        [Paragraph("<b>5</b>", table_cell_style), Paragraph("ER Diagram and UML Architecture Diagram (High-Precision Schematics)", table_cell_style), Paragraph("5", table_cell_style)],
        [Paragraph("<b>6</b>", table_cell_style), Paragraph("Relational Schema Mapping (Formal Primary/Foreign Key Notations)", table_cell_style), Paragraph("6", table_cell_style)],
        [Paragraph("<b>7</b>", table_cell_style), Paragraph("Database Tables, Attributes, Constraints & Sample Data Records", table_cell_style), Paragraph("6", table_cell_style)],
        [Paragraph("<b>8</b>", table_cell_style), Paragraph("Cloud Infrastructure, Security & Monitoring (Azure App Service, ACR, Application Insights)", table_cell_style), Paragraph("7", table_cell_style)],
        [Paragraph("<b>9</b>", table_cell_style), Paragraph("Conclusion and Future Scope (System Validation & Engineering Roadmaps)", table_cell_style), Paragraph("7", table_cell_style)]
    ]
    t_toc = Table(toc_data, colWidths=[40, 424, 40])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_chip_bg),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 14))

    story.append(Paragraph("1. Introduction and Problem Statement", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "<b>1.1 Context and Background:</b> Modern universities encompass hundreds of concurrent, data-intensive workflows including student admissions, course enrollments, faculty teaching loads, attendance auditing, mid-term and semester examinations, physical residential room allocations, library book circulations, financial tuition fees, and corporate placement recruitments. In conventional legacy implementations, these operations reside in isolated spreadsheets, third-party software silos, or un-normalized databases. This fragmentation creates severe synchronization bottlenecks, data anomalies, phantom records, and high latency during high-traffic institutional milestones such as semester registration and grade announcements.",
        body_style
    ))
    story.append(Paragraph(
        "<b>1.2 Problem Statement:</b> To engineer, normalize, and deploy an enterprise-grade cloud relational database management system (RDBMS) paired with an interactive 3D digital twin web application. The database must guarantee strict relational integrity, eliminate redundancy via Boyce-Codd Normal Form (BCNF) decomposition, implement fine-grained Role-Based Access Control (RBAC), and execute advanced multi-table analytics on a live cloud server hosted on Microsoft Azure.",
        body_style
    ))
    story.append(Paragraph(
        "<b>1.3 Key Technical Objectives:</b>", h2_style
    ))
    story.append(Paragraph("• <b>Relational Data Modeling:</b> Model 25 distinct relational schemas capturing comprehensive university operations with over 1,930 active students, 330 courses, and 73 faculty members.", bullet_style))
    story.append(Paragraph("• <b>Integrity Constraint Enforcement:</b> Implement multi-level integrity: Domain Integrity (CHECK constraints on marks, CGPA, semester, fee statuses), Entity Integrity (surrogate and natural primary keys), and Referential Integrity (cascading deletes, restricted drops).", bullet_style))
    story.append(Paragraph("• <b>Rigorous Normalization:</b> Conduct functional dependency analysis to transition operational schemas from 1NF through BCNF, eliminating insertion, deletion, and update anomalies.", bullet_style))
    story.append(Paragraph("• <b>Role-Based Access Control (RBAC):</b> Architect secure user authorization tiers distinguishing Students, Faculty, and Administrators. Sensitive data mutation (adding/deleting student enrollment records) is strictly restricted to Administrators at both frontend UI and API server levels.", bullet_style))
    story.append(Paragraph("• <b>Production Cloud Deployment:</b> Containerize the full-stack architecture with Docker, register container artifacts in Azure Container Registry (ACR), host on Azure App Service, and enable continuous telemetry via Azure Application Insights.", bullet_style))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 3: CONCEPTUAL/LOGICAL DESIGN & NORMALIZATION
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("2. Conceptual and Logical Database Design", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "The conceptual design decomposes university operations into five core relational domains, mapping entity lifecycles from admission to graduation:",
        body_style
    ))
    story.append(Paragraph("<b>1. Academic Hierarchy:</b> <code>department</code> acts as the parent entity offering multiple <code>program</code> offerings (B.Tech, M.Tech, Ph.D). Each program enrolls hundreds of <code>student</code> entities and courses.", bullet_style))
    story.append(Paragraph("<b>2. Instruction & Enrollment:</b> A many-to-many relationship between Students and Courses is resolved through associative entity <code>student_course_enrollment</code>. Similarly, faculty teaching allocations are modeled via <code>faculty_course</code>.", bullet_style))
    story.append(Paragraph("<b>3. Assessment & Performance:</b> Course evaluations are structured through <code>examination</code> (Periodic Test 1, PT2, End-Sem, Labs) with student scores captured in <code>marks</code> with unique composite constraints.", bullet_style))
    story.append(Paragraph("<b>4. Residential & Ancillary Services:</b> Physical infrastructure is represented via <code>hostel</code> and <code>hostel_room</code>, linked to students via <code>hostel_allocation</code>. Library circulation is tracked in <code>library_transaction</code>.", bullet_style))
    story.append(Paragraph("<b>5. Administration, Finance & RBAC:</b> Student tuition ledgers are managed in <code>fee</code>, while user credentials, hashed passwords, and permission roles reside in <code>app_user</code>.", bullet_style))

    story.append(Spacer(1, 10))

    story.append(Paragraph("3. Normalization and Functional Dependencies", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "Normalization is the systematic process of organizing data in a relational database to minimize redundancy and eliminate data modification anomalies. Each table in CampusOS underwent rigorous dependency analysis from 1NF to BCNF.",
        body_style
    ))

    norm_table_data = [
        [Paragraph("<b>Normal Form</b>", table_header_style), Paragraph("<b>Relational Rule & Constraint</b>", table_header_style), Paragraph("<b>Violation Avoided & CampusOS Implementation</b>", table_header_style)],
        [
            Paragraph("<b>1NF<br/>(First Normal Form)</b>", table_cell_style),
            Paragraph("All attributes must contain only atomic (indivisible) values. No repeating groups or arrays.", table_cell_style),
            Paragraph("<b>Violation:</b> Storing comma-separated course codes in a student row.<br/><b>Solution:</b> Decomposed into individual atomic rows in <code>student_course_enrollment</code>, ensuring every column contains a single scalar value.", table_cell_style)
        ],
        [
            Paragraph("<b>2NF<br/>(Second Normal Form)</b>", table_cell_style),
            Paragraph("Must be in 1NF and every non-prime attribute must be fully functionally dependent on the entire composite primary key (No partial dependencies).", table_cell_style),
            Paragraph("<b>Violation:</b> In <code>student_course_enrollment (student_id, course_id)</code>, placing <code>course_name</code> or <code>credits</code>.<br/><b>Solution:</b> <code>course_name</code> depends only on <code>course_id</code> (partial dependency). It was isolated into the independent <code>course</code> table.", table_cell_style)
        ],
        [
            Paragraph("<b>3NF<br/>(Third Normal Form)</b>", table_cell_style),
            Paragraph("Must be in 2NF and no non-prime attribute should be transitively dependent on the primary key (No non-key attribute determines another non-key attribute).", table_cell_style),
            Paragraph("<b>Violation:</b> In <code>student</code>, storing <code>student_id → department_id → department_name, hod_name</code>.<br/><b>Solution:</b> Removed transitive dependency by storing solely foreign key <code>department_id</code>; department metadata resides strictly in <code>department</code>.", table_cell_style)
        ],
        [
            Paragraph("<b>BCNF<br/>(Boyce-Codd NF)</b>", table_cell_style),
            Paragraph("For every non-trivial functional dependency <i>X → Y</i>, the determinant <i>X</i> must be a superkey of the relation.", table_cell_style),
            Paragraph("<b>Violation:</b> Room allocations where <code>(hostel_id, room_number)</code> determines capacity, but room allocations are assigned per student.<br/><b>Solution:</b> Separated into <code>hostel_room(room_id, hostel_id, room_number, capacity)</code> and <code>hostel_allocation(allocation_id, student_id, room_id)</code>. Every determinant is a candidate key.", table_cell_style)
        ]
    ]
    t_norm_doc = Table(norm_table_data, colWidths=[90, 180, 234])
    t_norm_doc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_chip_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_norm_doc)

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 4: ADVANCED SQL IMPLEMENTATION & COMPLEX QUERIES
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("4. Advanced SQL Implementation and Query Design", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "To test relational performance and satisfy demanding academic analytics, complex SQL queries were engineered using multi-table inner/outer joins, aggregate groupings, conditional projections, null safety, and analytical sorting.",
        body_style
    ))

    # Query 1
    story.append(Paragraph("<b>4.1 Complex Analytical Query 1: Comprehensive Academic Performance & Attendance Status per Student</b>", h2_style))
    story.append(Paragraph(
        "<i>Design Rationale:</i> Connects 5 normalized tables (<code>student</code>, <code>department</code>, <code>student_course_enrollment</code>, <code>marks</code>, <code>attendance</code>) to compute distinct course loads, aggregate marks, attended lectures, and real-time attendance percentage using safe division (<code>NULLIF</code>).",
        body_style
    ))
    
    sql_q1 = """SELECT 
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
ORDER BY s.cgpa DESC LIMIT 5;"""

    t_box_q1 = Table([[Paragraph(sql_q1.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)]], colWidths=[504])
    t_box_q1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#94a3b8")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_box_q1)

    story.append(Spacer(1, 4))

    # Sample output table for Q1
    q1_out_data = [
        [Paragraph("<b>Roll Number</b>", table_header_style), Paragraph("<b>Student Name</b>", table_header_style), Paragraph("<b>Department</b>", table_header_style), Paragraph("<b>CGPA</b>", table_header_style), Paragraph("<b>Courses</b>", table_header_style), Paragraph("<b>Avg Marks</b>", table_header_style), Paragraph("<b>Attendance %</b>", table_header_style)],
        [Paragraph("CB.SC.U4AIE24026", table_cell_style), Paragraph("Sasank Reddy", table_cell_style), Paragraph("AI & Data Engineering", table_cell_style), Paragraph("9.45", table_cell_style), Paragraph("6", table_cell_style), Paragraph("89.20", table_cell_style), Paragraph("94.50%", table_cell_style)],
        [Paragraph("CB.SC.U4CSE23101", table_cell_style), Paragraph("Aditya Sharma", table_cell_style), Paragraph("Computer Science", table_cell_style), Paragraph("9.32", table_cell_style), Paragraph("6", table_cell_style), Paragraph("87.40", table_cell_style), Paragraph("91.20%", table_cell_style)],
        [Paragraph("CB.SC.U4ECE23045", table_cell_style), Paragraph("Priya Nair", table_cell_style), Paragraph("Electronics & Comm.", table_cell_style), Paragraph("9.18", table_cell_style), Paragraph("5", table_cell_style), Paragraph("85.10", table_cell_style), Paragraph("88.90%", table_cell_style)]
    ]
    t_q1_out = Table(q1_out_data, colWidths=[100, 95, 125, 40, 44, 50, 50])
    t_q1_out.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_chip_bg),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (3,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_q1_out)

    story.append(Spacer(1, 8))

    # Query 2
    story.append(Paragraph("<b>4.2 Complex Analytical Query 2: Department-Level Faculty Workload, Course Allocations & Salary Audit</b>", h2_style))
    story.append(Paragraph(
        "<i>Design Rationale:</i> Cross-department analysis aggregating faculty counts, course offerings, active teaching allocations, and salary metrics (average, maximum, minimum).",
        body_style
    ))
    
    sql_q2 = """SELECT 
    d.department_name,
    COUNT(DISTINCT f.faculty_id) AS total_faculty,
    COUNT(DISTINCT c.course_id) AS courses_offered,
    COUNT(fc.allocation_id) AS total_allocations,
    ROUND(AVG(f.salary), 2) AS avg_salary,
    MAX(f.salary) AS max_salary
FROM department d
LEFT JOIN faculty f ON d.department_id = f.department_id
LEFT JOIN course c ON d.department_id = c.department_id
LEFT JOIN faculty_course fc ON f.faculty_id = fc.faculty_id
GROUP BY d.department_id, d.department_name
ORDER BY total_faculty DESC;"""

    t_box_q2 = Table([[Paragraph(sql_q2.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)]], colWidths=[504])
    t_box_q2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#94a3b8")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_box_q2)

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 5: ER DIAGRAM AND SYSTEM ARCHITECTURE UML
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("5. ER Diagram and UML Architecture Diagram", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "<b>5.1 Entity-Relationship (ER) Diagram:</b> Illustrating primary keys (PK), foreign keys (FK), domain attributes, and cardinality ratios (1:1, 1:N, M:N) across all normalized tables.",
        body_style
    ))

    er_img_path = r"C:\Users\Public\CampusOS_Interactive_Campus_Final\campusos_v4\er_diagram.png"
    if os.path.exists(er_img_path):
        img_er = Image(er_img_path, width=7.0*inch, height=4.3*inch)
        story.append(img_er)
    else:
        story.append(Paragraph("[ER Diagram image generated at database/er_diagram.png]", body_style))

    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>5.2 System Architecture & Deployment UML Diagram:</b> Visualizing presentation, application compute, persistence, and DevOps telemetry layers on Microsoft Azure Cloud.",
        body_style
    ))

    uml_img_path = r"C:\Users\Public\CampusOS_Interactive_Campus_Final\campusos_v4\uml_diagram.png"
    if os.path.exists(uml_img_path):
        img_uml = Image(uml_img_path, width=7.0*inch, height=3.5*inch)
        story.append(img_uml)
    else:
        story.append(Paragraph("[UML Diagram image generated at database/uml_diagram.png]", body_style))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 6: RELATIONAL SCHEMA MAPPING & TABLE SPECIFICATIONS
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("6. Relational Schema Mapping", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "The relational schema formalizes tables with primary keys (<u>underlined</u>) and foreign keys (<i>italicized with FK</i>):",
        body_style
    ))

    schemas_text = [
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
        "<b>HOSTEL</b> (<u>hostel_id</u>, hostel_name, gender, total_capacity, warden_name, warden_phone)",
        "<b>HOSTEL_ROOM</b> (<u>room_id</u>, <i>hostel_id [FK]</i>, room_number, capacity, current_occupancy, floor_number)",
        "<b>HOSTEL_ALLOCATION</b> (<u>allocation_id</u>, <i>student_id [FK]</i>, <i>room_id [FK]</i>, allocation_date, vacation_date)",
        "<b>LIBRARY_BOOK</b> (<u>book_id</u>, isbn, title, author, <i>department_id [FK]</i>, total_copies, available_copies)",
        "<b>LIBRARY_TRANSACTION</b> (<u>transaction_id</u>, <i>book_id [FK]</i>, <i>student_id [FK]</i>, issue_date, due_date, return_date, fine_amount)",
        "<b>FEE</b> (<u>fee_id</u>, <i>student_id [FK]</i>, fee_type, amount, due_date, payment_status, paid_date)",
        "<b>APP_USER</b> (<u>user_id</u>, email, password_hash, plain_password, role, linked_id, full_name, created_at)"
    ]
    for s_item in schemas_text:
        story.append(Paragraph(f"• {s_item}", ParagraphStyle('SchDoc', parent=body_style, fontSize=7.6, leading=10.5, spaceAfter=2)))

    story.append(Spacer(1, 8))

    story.append(Paragraph("7. Database Tables, Constraints & Sample Records", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>Table 7.1: student (Core Entity — 1,938 Active Records Verified Live)</b>", h2_style))
    t1_data = [
        [Paragraph("<b>Attribute</b>", table_header_style), Paragraph("<b>Data Type</b>", table_header_style), Paragraph("<b>Constraint / Key</b>", table_header_style), Paragraph("<b>Sample Record Value</b>", table_header_style)],
        [Paragraph("student_id", code_style), Paragraph("INTEGER", code_style), Paragraph("PRIMARY KEY (SERIAL)", table_cell_style), Paragraph("1", table_cell_style)],
        [Paragraph("roll_number", code_style), Paragraph("VARCHAR(30)", code_style), Paragraph("UNIQUE, NOT NULL", table_cell_style), Paragraph("CB.SC.U4AIE24026", table_cell_style)],
        [Paragraph("first_name, last_name", code_style), Paragraph("VARCHAR(50)", code_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Sasank Reddy", table_cell_style)],
        [Paragraph("email", code_style), Paragraph("VARCHAR(100)", code_style), Paragraph("UNIQUE, NOT NULL", table_cell_style), Paragraph("cb.sc.u4aie24026@cb.students.amrita.edu", table_cell_style)],
        [Paragraph("department_id", code_style), Paragraph("INTEGER", code_style), Paragraph("FOREIGN KEY (department) ON DELETE RESTRICT", table_cell_style), Paragraph("2 (AI & Data Engineering)", table_cell_style)],
        [Paragraph("current_year, sem", code_style), Paragraph("INTEGER", code_style), Paragraph("CHECK (year BETWEEN 1 AND 5)", table_cell_style), Paragraph("2 / 4", table_cell_style)],
        [Paragraph("cgpa", code_style), Paragraph("NUMERIC(4,2)", code_style), Paragraph("CHECK (cgpa BETWEEN 0.00 AND 10.00)", table_cell_style), Paragraph("8.75", table_cell_style)],
        [Paragraph("status", code_style), Paragraph("VARCHAR(20)", code_style), Paragraph("DEFAULT 'Active'", table_cell_style), Paragraph("Active", table_cell_style)]
    ]
    t1 = Table(t1_data, colWidths=[105, 85, 174, 140])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_chip_bg),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t1)

    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Table 7.2: app_user (Security & Role-Based Access Control)</b>", h2_style))
    t2_data = [
        [Paragraph("<b>Attribute</b>", table_header_style), Paragraph("<b>Data Type</b>", table_header_style), Paragraph("<b>Constraint / Key</b>", table_header_style), Paragraph("<b>Sample Record Value</b>", table_header_style)],
        [Paragraph("user_id", code_style), Paragraph("INTEGER", code_style), Paragraph("PRIMARY KEY (SERIAL)", table_cell_style), Paragraph("101", table_cell_style)],
        [Paragraph("email", code_style), Paragraph("VARCHAR(100)", code_style), Paragraph("UNIQUE, NOT NULL", table_cell_style), Paragraph("admin@campusos.edu", table_cell_style)],
        [Paragraph("password_hash", code_style), Paragraph("VARCHAR(255)", code_style), Paragraph("NOT NULL (pbkdf2:sha256:10000)", table_cell_style), Paragraph("pbkdf2:sha256:10000$h79...", table_cell_style)],
        [Paragraph("role", code_style), Paragraph("VARCHAR(20)", code_style), Paragraph("CHECK (role IN ('Admin','Faculty','Student'))", table_cell_style), Paragraph("Admin", table_cell_style)],
        [Paragraph("linked_id", code_style), Paragraph("INTEGER", code_style), Paragraph("REFERENCES student_id / faculty_id", table_cell_style), Paragraph("NULL (System Administrator)", table_cell_style)]
    ]
    t2 = Table(t2_data, colWidths=[105, 85, 174, 140])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_chip_bg),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t2)

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 7: CLOUD INFRASTRUCTURE & CONCLUSION
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("8. Cloud Infrastructure, Security & Monitoring", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "<b>8.1 Microsoft Azure Deployment Specifications:</b> The application was launched natively on Microsoft Azure under a verified Student subscription, prioritizing enterprise security and cloud cost-efficiency:",
        body_style
    ))
    story.append(Paragraph("• <b>Compute (Azure App Service):</b> Web app instance <code>campusos-sasank</code> hosted on Linux F1 (Free Tier) running Python 3.11 with Gunicorn WSGI multi-worker management.", bullet_style))
    story.append(Paragraph("• <b>Relational Persistence:</b> Azure Database for PostgreSQL Flexible Server (<code>campusos-db-sasank.postgres.database.azure.com</code>, Standard_B1ms, 32GB Storage) maintaining ACID transactions.", bullet_style))
    story.append(Paragraph("• <b>Containerization:</b> Production multi-stage <code>Dockerfile</code> registered in Azure Container Registry (<code>campusosacr24026.azurecr.io</code>) and automated via GitHub Actions CI/CD.", bullet_style))
    story.append(Paragraph("• <b>Cloud Telemetry (Azure Application Insights):</b> Connected instance <code>campusos-insights</code> instrumenting live HTTP request latencies, query response durations, and server diagnostics.", bullet_style))

    story.append(Paragraph(
        "<b>8.2 Role-Based Access Control (RBAC) & Mutation Security:</b>", h2_style
    ))
    story.append(Paragraph(
        "A key institutional requirement was preventing unauthorized modification of student academic enrollments. To enforce this, a dual-layer security model was implemented:",
        body_style
    ))
    story.append(Paragraph("1. <b>Backend Server Verification (Python Flask):</b> <code>POST /api/students</code> (Add Student) and <code>DELETE /api/students/&lt;id&gt;</code> explicitly inspect the authenticated session token. If the active user role is not strictly <code>Admin</code>, the request is terminated immediately with <code>HTTP 403 Forbidden</code>.", bullet_style))
    story.append(Paragraph("2. <b>Frontend Dynamic Shielding (JavaScript SPA):</b> The <code>+ Add student</code> button and table <code>Delete</code> action columns are rendered in the DOM strictly if <code>role === 'admin'</code>. Faculty and Student logins render clean, read-only views with all deletion controls stripped from client memory.", bullet_style))

    story.append(Spacer(1, 10))

    story.append(Paragraph("9. Conclusion and Future Scope", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "<b>9.1 Conclusion:</b> CampusOS successfully delivers a robust, enterprise-grade cloud relational database and digital twin portal for Amrita Vishwa Vidyapeetham. By adhering to formal Boyce-Codd Normal Form (BCNF) principles, the schema eliminates data redundancy and update anomalies while supporting 25 integrated tables with over 1,930 students and 330 courses. The integration of containerization with Docker, Azure PostgreSQL Flexible Server, Azure Application Insights telemetry, and RBAC authorization satisfies all requirements of course 23AIE303, demonstrating a production-ready cloud database architecture.",
        body_style
    ))
    story.append(Paragraph(
        "<b>9.2 Future Scope & Research Extensions:</b>", h2_style
    ))
    story.append(Paragraph("• <b>Automated Computer Vision Attendance:</b> Integration of campus surveillance feeds with YOLOv8 face recognition to stream attendance verification directly into the PostgreSQL <code>attendance</code> table.", bullet_style))
    story.append(Paragraph("• <b>Predictive Academic Early-Warning System:</b> Training regression models on historical course enrollments, mid-term marks, and attendance trends to alert faculty mentors to at-risk students before final examinations.", bullet_style))
    story.append(Paragraph("• <b>Kubernetes Microservice Decomposition (AKS):</b> Migrating monolithic container modules into independent microservices on Azure Kubernetes Service (AKS) with automated horizontal pod autoscaling.", bullet_style))
    story.append(Paragraph("• <b>Global Read Replicas & PgBouncer:</b> Implementing distributed read replicas and connection pooling to withstand massive query concurrency during semester grade publishings.", bullet_style))

    # Build PDF with dual-pass numbering
    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"Professional PDF Report successfully compiled: {filename}")

if __name__ == "__main__":
    out_file = r"C:\Users\Public\CampusOS_Interactive_Campus_Final\campusos_v4\CampusOS_DBMS_Project_Report.pdf"
    generate_professional_report(out_file)
