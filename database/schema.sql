-- ====================================================================
-- 23AIE303: Database Management Systems Project
-- Project: CampusOS - Smart Campus Digital Twin & Management System
-- Database: PostgreSQL 18 (university_digital_twin)
-- Cloud: Microsoft Azure PostgreSQL Flexible Server
-- ====================================================================

-- 1. DEPARTMENT
CREATE TABLE IF NOT EXISTS department (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_code VARCHAR(20) NOT NULL UNIQUE,
    hod_id INTEGER,
    established_year INTEGER CHECK (established_year >= 1950),
    contact_email VARCHAR(100)
);

-- 2. PROGRAM
CREATE TABLE IF NOT EXISTS program (
    program_id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES department(department_id) ON DELETE CASCADE,
    program_name VARCHAR(100) NOT NULL,
    degree_level VARCHAR(30) NOT NULL CHECK (degree_level IN ('Undergraduate', 'Postgraduate', 'Doctoral')),
    duration_years INTEGER NOT NULL CHECK (duration_years BETWEEN 1 AND 5),
    total_semesters INTEGER NOT NULL CHECK (total_semesters BETWEEN 2 AND 10)
);

-- 3. FACULTY
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES department(department_id) ON DELETE CASCADE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    designation VARCHAR(50) NOT NULL,
    joining_date DATE NOT NULL,
    qualification VARCHAR(100),
    specialization VARCHAR(100),
    salary NUMERIC(10, 2) CHECK (salary > 0)
);

-- 4. STUDENT
CREATE TABLE IF NOT EXISTS student (
    student_id SERIAL PRIMARY KEY,
    roll_number VARCHAR(30) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    dob DATE NOT NULL,
    department_id INTEGER NOT NULL REFERENCES department(department_id) ON DELETE RESTRICT,
    program_id INTEGER NOT NULL REFERENCES program(program_id) ON DELETE RESTRICT,
    admission_year INTEGER NOT NULL,
    current_year INTEGER CHECK (current_year BETWEEN 1 AND 5),
    current_semester INTEGER CHECK (current_semester BETWEEN 1 AND 10),
    cgpa NUMERIC(4, 2) DEFAULT 0.00 CHECK (cgpa >= 0.00 AND cgpa <= 10.00),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Graduated', 'Suspended', 'Withdrawn'))
);

-- 5. COURSE
CREATE TABLE IF NOT EXISTS course (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(150) NOT NULL,
    department_id INTEGER REFERENCES department(department_id) ON DELETE SET NULL,
    program_id INTEGER REFERENCES program(program_id) ON DELETE SET NULL,
    credits INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 10),
    semester_number INTEGER CHECK (semester_number BETWEEN 1 AND 10),
    course_type VARCHAR(30) DEFAULT 'Core' CHECK (course_type IN ('Core', 'Elective', 'Lab', 'Project'))
);

-- 6. FACULTY COURSE ALLOCATION
CREATE TABLE IF NOT EXISTS faculty_course (
    allocation_id SERIAL PRIMARY KEY,
    faculty_id INTEGER NOT NULL REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    academic_year VARCHAR(20) NOT NULL,
    semester_type VARCHAR(10) CHECK (semester_type IN ('Odd', 'Even')),
    UNIQUE (faculty_id, course_id, academic_year, semester_type)
);

-- 7. STUDENT COURSE ENROLLMENT
CREATE TABLE IF NOT EXISTS student_course_enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'Enrolled' CHECK (status IN ('Enrolled', 'Completed', 'Dropped')),
    UNIQUE (student_id, course_id)
);

-- 8. ATTENDANCE
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id BIGSERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(15) NOT NULL CHECK (status IN ('Present', 'Absent', 'On Duty')),
    marked_by INTEGER REFERENCES faculty(faculty_id) ON DELETE SET NULL
);

-- 9. EXAMINATION
CREATE TABLE IF NOT EXISTS examination (
    exam_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    exam_type VARCHAR(30) NOT NULL CHECK (exam_type IN ('Periodic Test 1', 'Periodic Test 2', 'End Semester', 'Assignment', 'Lab Exam')),
    exam_date DATE NOT NULL,
    max_marks NUMERIC(5, 2) NOT NULL CHECK (max_marks > 0),
    weightage_percent NUMERIC(5, 2) CHECK (weightage_percent BETWEEN 0 AND 100)
);

-- 10. MARKS
CREATE TABLE IF NOT EXISTS marks (
    mark_id BIGSERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    exam_id INTEGER NOT NULL REFERENCES examination(exam_id) ON DELETE CASCADE,
    marks_obtained NUMERIC(5, 2) NOT NULL CHECK (marks_obtained >= 0),
    grade VARCHAR(5),
    UNIQUE (student_id, exam_id)
);

-- 11. FEE
CREATE TABLE IF NOT EXISTS fee (
    fee_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    fee_type VARCHAR(50) NOT NULL CHECK (fee_type IN ('Tuition', 'Hostel', 'Library', 'Exam', 'Transport')),
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    due_date DATE NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'Pending' CHECK (payment_status IN ('Paid', 'Pending', 'Partial', 'Overdue')),
    paid_date DATE
);

-- 12. HOSTEL & HOSTEL ROOM
CREATE TABLE IF NOT EXISTS hostel (
    hostel_id SERIAL PRIMARY KEY,
    hostel_name VARCHAR(100) NOT NULL UNIQUE,
    gender VARCHAR(10) CHECK (gender IN ('Boys', 'Girls')),
    total_capacity INTEGER CHECK (total_capacity > 0),
    warden_name VARCHAR(100),
    warden_phone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS hostel_room (
    room_id SERIAL PRIMARY KEY,
    hostel_id INTEGER NOT NULL REFERENCES hostel(hostel_id) ON DELETE CASCADE,
    room_number VARCHAR(20) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    current_occupancy INTEGER DEFAULT 0 CHECK (current_occupancy >= 0),
    floor_number INTEGER DEFAULT 1,
    UNIQUE (hostel_id, room_number)
);

CREATE TABLE IF NOT EXISTS hostel_allocation (
    allocation_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL UNIQUE REFERENCES student(student_id) ON DELETE CASCADE,
    room_id INTEGER NOT NULL REFERENCES hostel_room(room_id) ON DELETE RESTRICT,
    allocation_date DATE DEFAULT CURRENT_DATE,
    vacation_date DATE
);

-- 13. LIBRARY
CREATE TABLE IF NOT EXISTS library_book (
    book_id SERIAL PRIMARY KEY,
    isbn VARCHAR(30) UNIQUE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(150) NOT NULL,
    department_id INTEGER REFERENCES department(department_id) ON DELETE SET NULL,
    total_copies INTEGER NOT NULL CHECK (total_copies >= 0),
    available_copies INTEGER NOT NULL CHECK (available_copies >= 0)
);

CREATE TABLE IF NOT EXISTS library_transaction (
    transaction_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES library_book(book_id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    issue_date DATE DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    fine_amount NUMERIC(8, 2) DEFAULT 0.00 CHECK (fine_amount >= 0)
);

-- 14. PLACEMENT
CREATE TABLE IF NOT EXISTS company (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL UNIQUE,
    industry_type VARCHAR(50),
    contact_email VARCHAR(100),
    tier VARCHAR(20) CHECK (tier IN ('Dream', 'Super Dream', 'Regular'))
);

CREATE TABLE IF NOT EXISTS placement_drive (
    drive_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES company(company_id) ON DELETE CASCADE,
    drive_date DATE NOT NULL,
    package_lpa NUMERIC(6, 2) CHECK (package_lpa > 0),
    min_cgpa NUMERIC(4, 2) CHECK (min_cgpa BETWEEN 0 AND 10),
    venue VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS placement_registration (
    registration_id SERIAL PRIMARY KEY,
    drive_id INTEGER NOT NULL REFERENCES placement_drive(drive_id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    status VARCHAR(30) DEFAULT 'Applied' CHECK (status IN ('Applied', 'Shortlisted', 'Interviewed', 'Offered', 'Rejected')),
    UNIQUE (drive_id, student_id)
);

-- 15. AUTHENTICATION & SECURITY
CREATE TABLE IF NOT EXISTS app_user (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    plain_password VARCHAR(100),
    role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'Faculty', 'Student')),
    linked_id INTEGER,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
