import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_uml():
    # 24 x 14 canvas at 300 DPI for crisp presentation quality
    fig, ax = plt.subplots(figsize=(24, 14), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Slide Title (exactly matching faculty slide style)
    ax.text(0.8, 13.1, "CLASS DIAGRAM", fontsize=32, weight="bold", color="#0b5394", fontfamily="sans-serif")
    ax.text(0.82, 12.65, "CampusOS DBMS — Academic Object-Oriented Domain Model & Relational Structure",
            fontsize=12, color="#475569", fontfamily="sans-serif")

    # Classes definitions matching faculty slide
    classes = [
        # --- Top Center: Base Class ---
        {
            "name": "User",
            "x": 8.5, "y": 9.8, "w": 5.2, "h": 2.7,
            "hdr_bg": "#d9d2e9", "hdr_border": "#8e7cc3", "text_color": "#2d1a47",
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
            "x": 18.5, "y": 10.2, "w": 4.5, "h": 2.3,
            "hdr_bg": "#f4cccc", "hdr_border": "#c27ba0", "text_color": "#4c1130",
            "attributes": [
                "- department_id: int (PK)",
                "- name: string (Unique)",
                "- hod_id: int (FK)"
            ],
            "methods": [
                "+ get_faculty(): List<Faculty>"
            ]
        },

        # --- Middle Row: Tops aligned at y=8.8 ---
        {
            "name": "Student",
            "x": 0.8, "y": 4.9, "w": 4.8, "h": 3.9,
            "hdr_bg": "#cfe2f3", "hdr_border": "#3d85c6", "text_color": "#073763",
            "attributes": [
                "- student_id: int (PK)",
                "- user_id: int (FK)",
                "- roll_number: string (Unique)",
                "- gender: string",
                "- dob: date",
                "- address: string",
                "- admission_date: date"
            ],
            "methods": [
                "+ view_profile(): Student",
                "+ view_courses(): List<Course>",
                "+ view_timetable(): List<Timetable>",
                "+ view_attendance(): List<Attendance>",
                "+ view_marks(): List<Mark>",
                "+ view_fees(): List<Payment>"
            ]
        },
        {
            "name": "Faculty",
            "x": 6.6, "y": 5.3, "w": 4.8, "h": 3.5,
            "hdr_bg": "#fce5cd", "hdr_border": "#e69138", "text_color": "#783f04",
            "attributes": [
                "- faculty_id: int (PK)",
                "- user_id: int (FK)",
                "- employee_id: string (Unique)",
                "- department_id: int (FK)",
                "- designation: string",
                "- hire_date: date"
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
            "x": 12.4, "y": 5.0, "w": 4.6, "h": 3.8,
            "hdr_bg": "#d9ead3", "hdr_border": "#6aa84f", "text_color": "#274e13",
            "attributes": [
                "- admin_id: int (PK)",
                "- user_id: int (FK)"
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
            "x": 18.5, "y": 5.8, "w": 4.5, "h": 3.0,
            "hdr_bg": "#d0e0e3", "hdr_border": "#45818e", "text_color": "#134f5c",
            "attributes": [
                "- course_id: int (PK)",
                "- department_id: int (FK)",
                "- code: string (Unique)",
                "- title: string",
                "- credits: int"
            ],
            "methods": [
                "+ get_faculty(): List<Faculty>",
                "+ get_students(): List<Student>"
            ]
        },

        # --- Bottom Row: Tops aligned at y=3.4 ---
        {
            "name": "Enrollment",
            "x": 0.8, "y": 1.0, "w": 3.8, "h": 2.4,
            "hdr_bg": "#f4cccc", "hdr_border": "#c27ba0", "text_color": "#4c1130",
            "attributes": [
                "- enrollment_id: int (PK)",
                "- student_id: int (FK)",
                "- course_id: int (FK)",
                "- semester: string",
                "- academic_year: string"
            ],
            "methods": []
        },
        {
            "name": "Payment",
            "x": 5.2, "y": 0.6, "w": 4.0, "h": 2.8,
            "hdr_bg": "#d9d2e9", "hdr_border": "#8e7cc3", "text_color": "#2d1a47",
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
                "+ record_payment(): void"
            ]
        },
        {
            "name": "Attendance",
            "x": 9.8, "y": 0.7, "w": 4.0, "h": 2.7,
            "hdr_bg": "#cfe2f3", "hdr_border": "#3d85c6", "text_color": "#073763",
            "attributes": [
                "- attendance_id: int (PK)",
                "- student_id: int (FK)",
                "- course_id: int (FK)",
                "- faculty_id: int (FK)",
                "- date: date",
                "- status: enum (Present, Absent)"
            ],
            "methods": [
                "+ mark(): void"
            ]
        },
        {
            "name": "Mark",
            "x": 14.4, "y": 0.4, "w": 4.2, "h": 3.0,
            "hdr_bg": "#fce5cd", "hdr_border": "#e69138", "text_color": "#783f04",
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
            "x": 19.2, "y": 0.9, "w": 3.8, "h": 2.5,
            "hdr_bg": "#f4cccc", "hdr_border": "#c27ba0", "text_color": "#4c1130",
            "attributes": [
                "- timetable_id: int (PK)",
                "- course_id: int (FK)",
                "- faculty_id: int (FK)",
                "- day: string",
                "- start_time: time",
                "- end_time: time",
                "- room: string"
            ],
            "methods": []
        }
    ]

    header_h = 0.42
    # Render all classes
    for c in classes:
        x, y, w, h = c["x"], c["y"], c["w"], c["h"]
        b_col = c["hdr_border"]
        
        # Outer box
        rect = patches.Rectangle((x, y), w, h, linewidth=1.3, edgecolor=b_col, facecolor='#ffffff')
        ax.add_patch(rect)
        
        # Header banner
        hdr = patches.Rectangle((x, y + h - header_h), w, header_h, linewidth=1.3,
                                edgecolor=b_col, facecolor=c["hdr_bg"])
        ax.add_patch(hdr)
        ax.text(x + w / 2, y + h - header_h / 2, c["name"],
                fontsize=11.5, weight="bold", color=c["text_color"], ha="center", va="center", fontfamily="sans-serif")
        
        # Compartments
        has_methods = len(c["methods"]) > 0
        attr_count = len(c["attributes"])
        meth_count = len(c["methods"])
        
        if has_methods:
            meth_space = meth_count * 0.22 + 0.14
            div_y = y + meth_space
            
            # Divider
            ax.plot([x, x + w], [div_y, div_y], color=b_col, linewidth=1.0)
            
            # Attributes
            attr_avail = (y + h - header_h) - div_y
            step_a = (attr_avail - 0.12) / attr_count
            for i, a in enumerate(c["attributes"]):
                ly = (y + h - header_h) - 0.18 - i * step_a
                ax.text(x + 0.15, ly, a, fontsize=7.6, color="#1e293b", fontfamily="sans-serif", va="center")
                
            # Methods
            step_m = (div_y - y - 0.1) / meth_count
            for j, m in enumerate(c["methods"]):
                ly = div_y - 0.14 - j * step_m
                ax.text(x + 0.15, ly, m, fontsize=7.6, color="#1e293b", fontfamily="sans-serif", va="center")
        else:
            avail = y + h - header_h - y
            step_a = (avail - 0.12) / attr_count
            for i, a in enumerate(c["attributes"]):
                ly = (y + h - header_h) - 0.18 - i * step_a
                ax.text(x + 0.15, ly, a, fontsize=7.6, color="#1e293b", fontfamily="sans-serif", va="center")

    # =========================================================
    # RELATIONSHIPS & MULTIPLICITY
    # =========================================================
    line_col = "#1f2937"
    lw = 1.3

    # 1. Inheritance (User -> Student, Faculty, Admin)
    # Hollow triangle at User bottom center (x=11.1, y=9.8)
    tri_tip = [11.1, 9.8]
    tri_left = [10.92, 9.5]
    tri_right = [11.28, 9.5]
    tri = patches.Polygon([tri_tip, tri_left, tri_right], closed=True,
                          facecolor="white", edgecolor=line_col, linewidth=lw)
    ax.add_patch(tri)

    # Vertical trunk from triangle base to horizontal branch bar
    ax.plot([11.1, 11.1], [9.5, 9.2], color=line_col, linewidth=lw)

    # Horizontal branch bar spanning Student center (3.2) to Admin center (14.7)
    ax.plot([3.2, 14.7], [9.2, 9.2], color=line_col, linewidth=lw)

    # Drops to subclass box tops at y=8.8
    ax.plot([3.2, 3.2], [9.2, 8.8], color=line_col, linewidth=lw)   # To Student
    ax.plot([9.0, 9.0], [9.2, 8.8], color=line_col, linewidth=lw)   # To Faculty
    ax.plot([14.7, 14.7], [9.2, 8.8], color=line_col, linewidth=lw) # To Admin

    # 2. Department associations
    # Department to Course (1 to *)
    ax.plot([20.75, 20.75], [10.2, 8.8], color=line_col, linewidth=lw)
    ax.text(20.95, 9.85, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(20.95, 9.15, "*", fontsize=11, weight="bold", color=line_col)

    # Department to Faculty (1 to *)
    # Line leaves Department left side (18.5, 11.3), goes left to 17.5,
    # goes down between Admin and Course to y=4.5, goes left under Admin to Faculty right side (11.4, 5.8)
    ax.plot([18.5, 17.5, 17.5, 11.4], [11.3, 11.3, 4.5, 4.5], color=line_col, linewidth=lw)
    ax.plot([11.4, 11.4], [4.5, 5.8], color=line_col, linewidth=lw)
    ax.text(18.15, 11.45, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(11.55, 5.95, "*", fontsize=11, weight="bold", color=line_col)

    # 3. Course associations
    # Course to Timetable (1 to *)
    ax.plot([21.1, 21.1], [5.8, 3.4], color=line_col, linewidth=lw)
    ax.text(21.25, 5.45, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(21.25, 3.75, "*", fontsize=11, weight="bold", color=line_col)

    # Course to Mark (1 to *)
    # Line from Course left edge (18.5, 6.3) to 18.0, down to 4.3, left to Mark top-right (17.5, 3.4)
    ax.plot([18.5, 18.0, 18.0, 17.5, 17.5], [6.3, 6.3, 4.3, 4.3, 3.4], color=line_col, linewidth=lw)
    ax.text(18.2, 6.45, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(17.65, 3.75, "*", fontsize=11, weight="bold", color=line_col)

    # 4. Student associations (Bottom Row)
    # Student to Enrollment (1 to *)
    # Leaves Student left edge (0.8, 6.6), goes left to 0.4, down to 3.7, right to Enrollment top (2.7, 3.4)
    ax.plot([0.8, 0.4, 0.4, 2.7, 2.7], [6.6, 6.6, 3.7, 3.7, 3.4], color=line_col, linewidth=lw)
    ax.text(0.55, 6.75, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(2.85, 3.75, "*", fontsize=11, weight="bold", color=line_col)

    # Student to Payment (1 to *)
    # Leaves Student bottom (3.8, 4.9), down to 4.1, right to Payment top (6.2, 3.4)
    ax.plot([3.8, 3.8, 6.2, 6.2], [4.9, 4.1, 4.1, 3.4], color=line_col, linewidth=lw)
    ax.text(3.95, 4.65, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(6.35, 3.75, "*", fontsize=11, weight="bold", color=line_col)

    # Student to Attendance (1 to *)
    # Leaves Student bottom (4.6, 4.9), down to 3.9, right to Attendance top (10.6, 3.4)
    ax.plot([4.6, 4.6, 10.6, 10.6], [4.9, 3.9, 3.9, 3.4], color=line_col, linewidth=lw)
    ax.text(4.75, 4.65, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(10.75, 3.75, "*", fontsize=11, weight="bold", color=line_col)

    # Student to Mark (1 to *)
    # Leaves Student bottom (5.2, 4.9), down to 3.7, right to Mark top (15.0, 3.4)
    ax.plot([5.2, 5.2, 15.0, 15.0], [4.9, 3.7, 3.7, 3.4], color=line_col, linewidth=lw)
    ax.text(5.35, 4.65, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(15.15, 3.75, "*", fontsize=11, weight="bold", color=line_col)

    # 5. Faculty associations (Bottom Row)
    # Faculty to Attendance (1 to *)
    # Leaves Faculty bottom (7.8, 5.3), down to 4.3, right to Attendance top (11.8, 3.4)
    ax.plot([7.8, 7.8, 11.8, 11.8], [5.3, 4.3, 4.3, 3.4], color=line_col, linewidth=lw)
    ax.text(7.95, 5.05, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(11.95, 3.75, "*", fontsize=11, weight="bold", color=line_col)

    # Faculty to Mark (1 to *)
    # Leaves Faculty bottom (9.8, 5.3), down to 4.2, right to Mark top (16.2, 3.4)
    ax.plot([9.8, 9.8, 16.2, 16.2], [5.3, 4.2, 4.2, 3.4], color=line_col, linewidth=lw)
    ax.text(9.95, 5.05, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(16.35, 3.75, "*", fontsize=11, weight="bold", color=line_col)

    # Faculty to Timetable (1 to *)
    # Leaves Faculty right side (11.4, 6.2), down under Admin at y=4.7, across to Timetable top (20.0, 3.4)
    ax.plot([11.4, 12.0, 12.0, 20.0, 20.0], [6.2, 6.2, 4.7, 4.7, 3.4], color=line_col, linewidth=lw)
    ax.text(11.55, 6.35, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(20.15, 3.75, "*", fontsize=11, weight="bold", color=line_col)

    # 6. Horizontal class relationships
    # Enrollment to Payment
    ax.plot([4.6, 5.2], [2.2, 2.2], color=line_col, linewidth=lw)
    ax.text(4.75, 2.35, "*", fontsize=11, weight="bold", color=line_col)
    ax.text(5.05, 2.35, "1", fontsize=9.5, weight="bold", color=line_col)

    # Attendance to Mark
    ax.plot([13.8, 14.4], [2.2, 2.2], color=line_col, linewidth=lw)
    ax.text(13.95, 2.35, "1", fontsize=9.5, weight="bold", color=line_col)
    ax.text(14.25, 2.35, "*", fontsize=11, weight="bold", color=line_col)

    # =========================================================
    # LEGEND BOX (Top Left, perfectly positioned)
    # =========================================================
    leg_x, leg_y, leg_w, leg_h = 0.8, 9.8, 4.8, 2.2
    leg = patches.FancyBboxPatch((leg_x, leg_y), leg_w, leg_h, boxstyle="round,pad=0,rounding_size=0.08",
                                 linewidth=1.2, edgecolor="#94a3b8", facecolor="#f8fafc")
    ax.add_patch(leg)
    ax.text(leg_x + 0.25, leg_y + leg_h - 0.35, "LEGEND & NOTATIONS", fontsize=10.5, weight="bold", color="#1e293b", fontfamily="sans-serif")
    
    # Legend items
    ax.text(leg_x + 0.25, leg_y + 1.40, "PK: Primary Key", fontsize=8.5, weight="bold", color="#0f172a", fontfamily="sans-serif")
    ax.text(leg_x + 2.5, leg_y + 1.40, "FK: Foreign Key", fontsize=8.5, color="#475569", fontfamily="sans-serif")
    ax.text(leg_x + 0.25, leg_y + 0.95, "1 : Exactly One", fontsize=8.5, color="#0f172a", fontfamily="sans-serif")
    ax.text(leg_x + 2.5, leg_y + 0.95, "* : Zero or Many", fontsize=8.5, color="#0f172a", fontfamily="sans-serif")
    
    # Symbols in Legend
    leg_tri = patches.Polygon([[leg_x + 0.45, leg_y + 0.55], [leg_x + 0.30, leg_y + 0.25], [leg_x + 0.60, leg_y + 0.25]],
                              closed=True, facecolor="white", edgecolor=line_col, linewidth=1.2)
    ax.add_patch(leg_tri)
    ax.text(leg_x + 0.75, leg_y + 0.35, "Inheritance (Generalization)", fontsize=8.0, color="#1e293b", fontfamily="sans-serif")
    
    ax.plot([leg_x + 2.5, leg_x + 2.9], [leg_y + 0.38, leg_y + 0.38], color=line_col, linewidth=1.3)
    ax.text(leg_x + 3.05, leg_y + 0.35, "Association", fontsize=8.0, color="#1e293b", fontfamily="sans-serif")

    # Canvas bounds
    ax.set_xlim(0, 24.0)
    ax.set_ylim(0, 14.0)
    ax.axis('off')
    plt.tight_layout()

    out_file = "C:/Users/Public/CampusOS_Interactive_Campus_Final/campusos_v4/uml_diagram.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print("Proper UML Class Diagram generated successfully at:", out_file)

if __name__ == "__main__":
    generate_uml()
