-- ====================================================================
-- 23AIE303: Advanced SQL Queries & Query Design
-- Demonstrating Multi-Table Joins, Aggregate Functions, GROUP BY,
-- Window Functions, and Subqueries
-- ====================================================================

-- Query 1: Comprehensive Academic Performance & Attendance Status per Student
-- Joins 6 tables with aggregation, conditional counting, and percentage calculation
SELECT 
    s.roll_number,
    s.first_name || ' ' || s.last_name AS student_name,
    d.department_name,
    p.program_name,
    s.cgpa,
    COUNT(DISTINCT sce.course_id) AS enrolled_courses,
    ROUND(AVG(m.marks_obtained), 2) AS avg_marks_obtained,
    COUNT(a.attendance_id) AS total_sessions,
    COUNT(CASE WHEN a.status = 'Present' THEN 1 END) AS attended_sessions,
    ROUND((COUNT(CASE WHEN a.status = 'Present' THEN 1 END)::numeric / NULLIF(COUNT(a.attendance_id), 0)) * 100, 2) AS attendance_percentage
FROM student s
JOIN department d ON s.department_id = d.department_id
JOIN program p ON s.program_id = p.program_id
LEFT JOIN student_course_enrollment sce ON s.student_id = sce.student_id
LEFT JOIN marks m ON s.student_id = m.student_id
LEFT JOIN attendance a ON s.student_id = a.student_id
WHERE s.status = 'Active'
GROUP BY s.student_id, s.roll_number, s.first_name, s.last_name, d.department_name, p.program_name, s.cgpa
HAVING COUNT(DISTINCT sce.course_id) > 0
ORDER BY s.cgpa DESC
LIMIT 20;

-- Query 2: Department-Level Faculty Workload, Course Distribution & Salary Analytics
SELECT 
    d.department_name,
    COUNT(DISTINCT f.faculty_id) AS total_faculty,
    COUNT(DISTINCT c.course_id) AS courses_offered,
    COUNT(fc.allocation_id) AS total_course_allocations,
    ROUND(AVG(f.salary), 2) AS avg_faculty_salary,
    MAX(f.salary) AS max_faculty_salary,
    MIN(f.salary) AS min_faculty_salary
FROM department d
LEFT JOIN faculty f ON d.department_id = f.department_id
LEFT JOIN course c ON d.department_id = c.department_id
LEFT JOIN faculty_course fc ON f.faculty_id = fc.faculty_id
GROUP BY d.department_id, d.department_name
ORDER BY total_faculty DESC;

-- Query 3: Hostel Occupancy, Vacancy & Resident Distribution
SELECT 
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
ORDER BY occupancy_rate DESC;

-- Query 4: Outstanding Fees and Financial Clearance Status per Department
SELECT 
    d.department_name,
    COUNT(DISTINCT s.student_id) AS total_students,
    SUM(f.amount) AS total_fee_assessed,
    SUM(CASE WHEN f.payment_status = 'Paid' THEN f.amount ELSE 0 END) AS total_fee_collected,
    SUM(CASE WHEN f.payment_status IN ('Pending', 'Overdue', 'Partial') THEN f.amount ELSE 0 END) AS pending_defaulter_amount,
    COUNT(CASE WHEN f.payment_status IN ('Pending', 'Overdue') THEN 1 END) AS pending_invoices
FROM department d
JOIN student s ON d.department_id = s.department_id
JOIN fee f ON s.student_id = f.student_id
GROUP BY d.department_id, d.department_name
ORDER BY pending_defaulter_amount DESC;

-- Query 5: Placement Eligibility and Drive Conversion Analytics
SELECT 
    c.company_name,
    c.tier,
    pd.package_lpa,
    pd.min_cgpa,
    COUNT(pr.student_id) AS total_applicants,
    COUNT(CASE WHEN pr.status = 'Offered' THEN 1 END) AS offers_made,
    ROUND((COUNT(CASE WHEN pr.status = 'Offered' THEN 1 END)::numeric / NULLIF(COUNT(pr.student_id), 0)) * 100, 2) AS selection_rate
FROM placement_drive pd
JOIN company c ON pd.company_id = c.company_id
LEFT JOIN placement_registration pr ON pd.drive_id = pr.drive_id
GROUP BY pd.drive_id, c.company_name, c.tier, pd.package_lpa, pd.min_cgpa
ORDER BY pd.package_lpa DESC;
