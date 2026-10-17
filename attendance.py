from db_connect import get_connection
from datetime import date

# Mark Attendance by Teacher
def mark_attendance(student_roll_no, subject_id, teacher_id, status):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        today = date.today()
        # Check if already marked today
        cursor.execute(
            "SELECT * FROM attendance WHERE student_roll_no=%s AND subject_id=%s AND date=%s",
            (student_roll_no, subject_id, today)
        )
        if cursor.fetchone():
            print("❌ Attendance already marked for this student today!")
        else:
            cursor.execute(
                "INSERT INTO attendance(student_roll_no, subject_id, teacher_id, date, status) VALUES(%s,%s,%s,%s,%s)",
                (student_roll_no, subject_id, teacher_id, today, status)
            )
            conn.commit()
            print(f"✅ Attendance marked: Student {student_roll_no} - {status}")
        conn.close()
    except Exception as e:
        print("⚠️ Error in mark_attendance:", e)

# View Attendance by Student
def view_attendance_by_student(student_roll_no):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT a.date, s.name AS subject, a.status FROM attendance a "
            "JOIN subjects s ON a.subject_id=s.id "
            "WHERE a.student_roll_no=%s ORDER BY a.date",
            (student_roll_no,)
        )
        rows = cursor.fetchall()
        conn.close()
        if rows:
            print(f"\n📋 Attendance for Student {student_roll_no}:")
            for row in rows:
                print(f"Date: {row[0]} | Subject: {row[1]} | Status: {row[2]}")
        else:
            print("❌ No attendance found for this student!")
    except Exception as e:
        print("⚠️ Error in view_attendance_by_student:", e)

# Teacher Attendance Menu
def teacher_attendance_menu(teacher_id):
    while True:
        print("\n--- Teacher Attendance Menu ---")
        print("1. Mark Attendance")
        print("2. View Student Attendance")
        print("3. Back")
        choice = input("Enter choice: ")

        if choice == "1":
            student_roll_no = input("Enter Student Roll No: ")
            subject_id = input("Enter Subject ID: ")
            status = input("Enter Status (Present/Absent): ")
            mark_attendance(student_roll_no, subject_id, teacher_id, status)

        elif choice == "2":
            student_roll_no = input("Enter Student Roll No to view: ")
            view_attendance_by_student(student_roll_no)

        elif choice == "3":
            print("Exiting Teacher Attendance Menu...")
            break

        else:
            print("❌ Invalid Choice")

# Student Attendance Menu
def student_attendance_menu(student_roll_no):
    try:
        print(f"\n--- Attendance for Student {student_roll_no} ---")
        view_attendance_by_student(student_roll_no)
    except Exception as e:
        print("⚠️ Error in student_attendance_menu:", e)
