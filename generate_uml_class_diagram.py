import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_uml_class_diagram():
    fig, ax = plt.subplots(figsize=(18, 12), dpi=300)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#ffffff')

    # Classes definition
    # Each class has: name, x, y, w, h, header_color, attributes, methods
    classes = [
        # --- Top Row: Base Class ---
        {
            "name": "User",
            "x": 6.8, "y": 8.7, "w": 3.6, "h": 2.7,
            "header_color": "#6366f1", # Indigo
            "attributes": [
                "- user_id: int (PK)",
                "- name: string",
                "- email: string (Unique)",
                "- password_hash: string",
                "- role: enum (Student, Faculty, Admin)",
                "- phone: string",
                "- created_at: datetime"
            ],
            "methods": [
                "+ login(email, password): bool",
                "+ logout(): void"
            ]
        },
        # --- Top Right: Department ---
        {
            "name": "Department",
            "x": 13.8, "y": 8.7, "w": 3.6, "h": 2.6,
            "header_color": "#e11d48", # Rose Red
            "attributes": [
                "- department_id: int (PK)",
                "- name: string (Unique)",
                "- code: string (Unique)",
                "- hod_id: int (FK)",
                "- established_year: int"
            ],
            "methods": [
                "+ get_faculty(): List<Faculty>",
                "+ get_courses(): List<Course>",
                "+ get_students(): List<Student>"
            ]
        },

        # --- Middle Row: Subclasses of User + Course ---
        {
            "name": "Student",
            "x": 0.8, "y": 4.8, "w": 3.6, "h": 3.3,
            "header_color": "#0284c7", # Sky Blue
            "attributes": [
                "- student_id: int (PK)",
                "- user_id: int (FK)",
                "- roll_number: string (Unique)",
                "- department_id: int (FK)",
                "- program_id: int (FK)",
                "- gender: string",
                "- dob: date",
                "- cgpa: decimal(4,2)",
                "- admission_year: int"
            ],
            "methods": [
                "+ view_profile(): Student",
                "+ view_courses(): List<Course>",
                "+ view_attendance(): List<Attendance>",
                "+ view_marks(): List<Mark>",
                "+ view_fees(): List<Payment>"
            ]
        },
        {
            "name": "Faculty",
            "x": 5.2, "y": 4.8, "w": 3.6, "h": 3.1,
            "header_color": "#d97706", # Amber
            "attributes": [
                "- faculty_id: int (PK)",
                "- user_id: int (FK)",
                "- employee_id: string (Unique)",
                "- department_id: int (FK)",
                "- designation: string",
                "- hire_date: date",
                "- salary: decimal(10,2)"
            ],
            "methods": [
                "+ view_profile(): Faculty",
                "+ view_assigned_courses(): List<Course>",
                "+ mark_attendance(): void",
                "+ enter_marks(): void"
            ]
        },
        {
            "name": "Admin",
            "x": 9.5, "y": 4.8, "w": 3.6, "h": 3.1,
            "header_color": "#059669", # Emerald Green
            "attributes": [
                "- admin_id: int (PK)",
                "- user_id: int (FK)",
                "- permissions: string[]"
            ],
            "methods": [
                "+ manage_students(): void",
                "+ manage_faculty(): void",
                "+ manage_courses(): void",
                "+ manage_departments(): void",
                "+ manage_fees(): void",
                "+ view_reports(): void",
                "+ manage_system_users(): void"
            ]
        },
        {
            "name": "Course",
            "x": 13.8, "y": 4.8, "w": 3.6, "h": 3.0,
            "header_color": "#0d9488", # Teal
            "attributes": [
                "- course_id: int (PK)",
                "- department_id: int (FK)",
                "- code: string (Unique)",
                "- title: string",
                "- credits: int",
                "- semester_number: int",
                "- course_type: string"
            ],
            "methods": [
                "+ get_faculty(): List<Faculty>",
                "+ get_students(): List<Student>"
            ]
        },

        # --- Bottom Row: Transactional / Entity Classes ---
        {
            "name": "Enrollment",
            "x": 0.6, "y": 0.7, "w": 3.1, "h": 2.6,
            "header_color": "#db2777", # Pink
            "attributes": [
                "- enrollment_id: int (PK)",
                "- student_id: int (FK)",
                "- course_id: int (FK)",
                "- semester: string",
                "- academic_year: string",
                "- status: string"
            ],
            "methods": [
                "+ enroll(): bool",
                "+ drop_course(): void"
            ]
        },
        {
            "name": "Payment",
            "x": 4.0, "y": 0.7, "w": 3.1, "h": 2.7,
            "header_color": "#7c3aed", # Purple
            "attributes": [
                "- payment_id: int (PK)",
                "- student_id: int (FK)",
                "- fee_type: string",
                "- amount: decimal(10,2)",
                "- due_date: date",
                "- paid_date: date (nullable)",
                "- status: enum (Paid, Pending)"
            ],
            "methods": [
                "+ record_payment(): void",
                "+ get_receipt(): Receipt"
            ]
        },
        {
            "name": "Attendance",
            "x": 7.4, "y": 0.7, "w": 3.1, "h": 2.6,
            "header_color": "#2563eb", # Blue
            "attributes": [
                "- attendance_id: int (PK)",
                "- student_id: int (FK)",
                "- course_id: int (FK)",
                "- faculty_id: int (FK)",
                "- date: date",
                "- status: enum (Present, Absent)"
            ],
            "methods": [
                "+ mark(): void",
                "+ get_percentage(): float"
            ]
        },
        {
            "name": "Mark",
            "x": 10.8, "y": 0.7, "w": 3.1, "h": 2.9,
            "header_color": "#d97706", # Amber
            "attributes": [
                "- mark_id: int (PK)",
                "- student_id: int (FK)",
                "- course_id: int (FK)",
                "- faculty_id: int (FK)",
                "- exam_type: string",
                "- marks_obtained: float",
                "- total_marks: float",
                "- grade: string"
            ],
            "methods": [
                "+ calculate_grade(): string"
            ]
        },
        {
            "name": "Timetable",
            "x": 14.2, "y": 0.7, "w": 3.1, "h": 2.7,
            "header_color": "#ea580c", # Rust / Orange
            "attributes": [
                "- timetable_id: int (PK)",
                "- course_id: int (FK)",
                "- faculty_id: int (FK)",
                "- day: string",
                "- start_time: time",
                "- end_time: time",
                "- room: string"
            ],
            "methods": [
                "+ allocate_slot(): void",
                "+ check_conflict(): bool"
            ]
        }
    ]

    # Render each class box (3 compartments)
    header_h = 0.42
    for c in classes:
        x, y, w, h = c["x"], c["y"], c["w"], c["h"]
        
        # Outer border
        outer = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08",
                                       facecolor="#ffffff", edgecolor="#475569", linewidth=1.4)
        ax.add_patch(outer)
        
        # Header Box
        hdr = patches.FancyBboxPatch((x, y + h - header_h), w, header_h,
                                     boxstyle="round,pad=0,rounding_size=0.08",
                                     facecolor=c["header_color"], edgecolor=c["header_color"], linewidth=1.2)
        ax.add_patch(hdr)
        ax.text(x + w / 2, y + h - header_h / 2, c["name"], color="white", weight="bold",
                fontsize=9.5, ha="center", va="center")
        
        # Attributes compartment
        attr_count = len(c["attributes"])
        attr_box_h = 0.23 * attr_count + 0.15
        attr_top = y + h - header_h
        
        for idx, attr in enumerate(c["attributes"]):
            line_y = attr_top - 0.18 - idx * 0.22
            # Highlight PK / FK with subtle weight
            color = "#1e293b"
            weight = "bold" if "(PK)" in attr else "normal"
            ax.text(x + 0.15, line_y, attr, fontsize=7.2, color=color, weight=weight, fontfamily="monospace", va="center")
            
        # Divider Line between Attributes & Methods
        div_y = y + len(c["methods"]) * 0.22 + 0.18
        ax.plot([x, x + w], [div_y, div_y], color="#cbd5e1", linewidth=1.0)
        
        # Methods compartment
        for idx, meth in enumerate(c["methods"]):
            line_y = div_y - 0.16 - idx * 0.21
            ax.text(x + 0.15, line_y, meth, fontsize=7.2, color="#334155", fontfamily="monospace", va="center")

    # -------------------------------------------------------------
    # RELATIONSHIPS & INHERITANCE
    # -------------------------------------------------------------
    
    # 1. Inheritance (Generalization: Student, Faculty, Admin -> User)
    # Hollow triangle at User base (x=8.6, y=8.7)
    triangle = patches.Polygon([[8.6, 8.7], [8.48, 8.45], [8.72, 8.45]],
                               closed=True, facecolor="white", edgecolor="#475569", linewidth=1.5)
    ax.add_patch(triangle)
    
    # Trunk line from triangle base down to y=8.25
    ax.plot([8.6, 8.6], [8.45, 8.25], color="#475569", linewidth=1.5)
    
    # Horizontal branch bar from Student(x=2.6) to Admin(x=11.3)
    ax.plot([2.6, 11.3], [8.25, 8.25], color="#475569", linewidth=1.5)
    
    # Drops to Student, Faculty, Admin
    ax.plot([2.6, 2.6], [8.25, 8.1], color="#475569", linewidth=1.5) # to Student
    ax.plot([7.0, 7.0], [8.25, 7.9], color="#475569", linewidth=1.5) # to Faculty
    ax.plot([11.3, 11.3], [8.25, 7.9], color="#475569", linewidth=1.5) # to Admin

    # 2. Department to Course (1 -> *)
    ax.plot([15.6, 15.6], [8.7, 7.8], color="#0f172a", linewidth=1.3)
    ax.text(15.75, 8.4, "1", fontsize=8, weight="bold", color="#0f172a")
    ax.text(15.75, 7.95, "*", fontsize=9, weight="bold", color="#0f172a")
    ax.text(15.65, 8.2, "offers", fontsize=7.2, style="italic", color="#475569")

    # 3. Department to Faculty (1 -> *)
    # Line from Department bottom-left to Faculty top-right
    ax.plot([13.8, 8.8, 8.8, 8.8], [9.3, 9.3, 8.0, 7.9], color="#0f172a", linewidth=1.3, linestyle="--")
    ax.text(13.5, 9.4, "1", fontsize=8, weight="bold", color="#0f172a")
    ax.text(8.9, 8.0, "*", fontsize=9, weight="bold", color="#0f172a")
    ax.text(11.0, 9.45, "employs", fontsize=7.2, style="italic", color="#475569")

    # 4. Student Associations to Bottom Row
    # Student -> Enrollment
    ax.plot([2.1, 2.1], [4.8, 3.3], color="#0f172a", linewidth=1.3)
    ax.text(2.2, 4.55, "1", fontsize=8, weight="bold")
    ax.text(2.2, 3.45, "*", fontsize=9, weight="bold")

    # Student -> Payment
    ax.plot([2.6, 2.6, 5.5, 5.5], [4.8, 4.1, 4.1, 3.4], color="#0f172a", linewidth=1.3)
    ax.text(2.7, 4.55, "1", fontsize=8, weight="bold")
    ax.text(5.6, 3.55, "*", fontsize=9, weight="bold")
    ax.text(4.0, 4.2, "pays", fontsize=7.2, style="italic", color="#475569")

    # Student -> Attendance
    ax.plot([3.1, 3.1, 8.5, 8.5], [4.8, 3.8, 3.8, 3.3], color="#0f172a", linewidth=1.3)
    ax.text(3.2, 4.55, "1", fontsize=8, weight="bold")
    ax.text(8.6, 3.45, "*", fontsize=9, weight="bold")

    # Student -> Mark
    ax.plot([3.6, 3.6, 11.5, 11.5], [4.8, 3.6, 3.6, 3.6], color="#0f172a", linewidth=1.3)
    ax.text(3.7, 4.55, "1", fontsize=8, weight="bold")
    ax.text(11.6, 3.75, "*", fontsize=9, weight="bold")
    ax.text(7.5, 3.45, "receives", fontsize=7.2, style="italic", color="#475569")

    # 5. Course Associations
    # Course -> Enrollment
    ax.plot([14.5, 14.5, 1.5, 1.5], [4.8, 4.4, 4.4, 3.3], color="#0f172a", linewidth=1.3, linestyle=":")
    ax.text(14.3, 4.55, "1", fontsize=8, weight="bold")
    ax.text(1.6, 3.45, "*", fontsize=9, weight="bold")

    # Course -> Timetable
    ax.plot([15.6, 15.6], [4.8, 3.4], color="#0f172a", linewidth=1.3)
    ax.text(15.75, 4.55, "1", fontsize=8, weight="bold")
    ax.text(15.75, 3.55, "*", fontsize=9, weight="bold")

    # Course -> Mark
    ax.plot([14.2, 14.2, 12.8, 12.8], [4.8, 4.0, 4.0, 3.6], color="#0f172a", linewidth=1.3)
    ax.text(14.0, 4.55, "1", fontsize=8, weight="bold")
    ax.text(12.9, 3.75, "*", fontsize=9, weight="bold")

    # 6. Faculty Associations
    # Faculty -> Attendance (mark attendance)
    ax.plot([7.0, 7.0, 9.2, 9.2], [4.8, 4.2, 4.2, 3.3], color="#0f172a", linewidth=1.3)
    ax.text(7.1, 4.55, "1", fontsize=8, weight="bold")
    ax.text(9.3, 3.45, "*", fontsize=9, weight="bold")

    # Faculty -> Timetable (teaches)
    ax.plot([7.8, 7.8, 15.0, 15.0], [4.8, 3.9, 3.9, 3.4], color="#0f172a", linewidth=1.3)
    ax.text(7.9, 4.55, "1", fontsize=8, weight="bold")
    ax.text(15.1, 3.55, "*", fontsize=9, weight="bold")
    ax.text(12.0, 4.0, "teaches", fontsize=7.2, style="italic", color="#475569")

    # -------------------------------------------------------------
    # LEGEND BOX (Bottom Left)
    # -------------------------------------------------------------
    leg_x, leg_y, leg_w, leg_h = 0.6, 3.6, 2.8, 1.05
    leg_box = patches.FancyBboxPatch((leg_x, leg_y), leg_w, leg_h, boxstyle="square,pad=0",
                                     facecolor="#f8fafc", edgecolor="#94a3b8", linewidth=1.2)
    ax.add_patch(leg_box)
    ax.text(leg_x + 0.15, leg_y + leg_h - 0.22, "LEGEND", fontsize=8.5, weight="bold", color="#0f172a")
    
    # Legend items
    ax.text(leg_x + 0.15, leg_y + 0.58, "PK: Primary Key", fontsize=7.2, weight="bold", color="#1e293b")
    ax.text(leg_x + 1.45, leg_y + 0.58, "FK: Foreign Key", fontsize=7.2, color="#475569")
    
    # Triangles / Arrows in Legend
    leg_tri = patches.Polygon([[leg_x + 0.25, leg_y + 0.35], [leg_x + 0.15, leg_y + 0.2], [leg_x + 0.35, leg_y + 0.2]],
                              closed=True, facecolor="white", edgecolor="#475569", linewidth=1.2)
    ax.add_patch(leg_tri)
    ax.text(leg_x + 0.45, leg_y + 0.24, "Inheritance (Generalization)", fontsize=7.0, color="#1e293b")
    
    ax.plot([leg_x + 0.15, leg_x + 0.35], [leg_y + 0.08, leg_y + 0.08], color="#0f172a", linewidth=1.2)
    ax.text(leg_x + 0.45, leg_y + 0.06, "Association (1 to *)", fontsize=7.0, color="#1e293b")

    # Main Title
    plt.title("CampusOS Database Management System — Formal UML Class Diagram",
              fontsize=14, weight="bold", pad=20, color="#0f172a")
    
    ax.set_xlim(0, 18.0)
    ax.set_ylim(0, 12.0)
    ax.axis('off')
    plt.tight_layout()

    out_path = "C:/Users/Public/CampusOS_Interactive_Campus_Final/campusos_v4/uml_diagram.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Formal UML Class Diagram generated successfully at:", out_path)

if __name__ == "__main__":
    generate_uml_class_diagram()
