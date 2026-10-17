from db_connect import get_connection
from attendance import view_attendance_by_student

# ----------------- TEACHER -----------------
def teacher_signup():
    try:
        print("\n--- Teacher Sign Up ---")
        name = input("Enter Name: ")
        email = input("Enter Email: ")
        password = input("Enter Password: ")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teachers WHERE email=%s", (email,))
        if cursor.fetchone():
            print("Teacher with this email already exists!")
            conn.close()
            return None

        cursor.execute(
            "INSERT INTO teachers(name, email, password, status) VALUES(%s,%s,%s,'Pending')",
            (name, email, password)
        )
        conn.commit()
        conn.close()
        print("Teacher registered! Admin approval pending.")
        return True
    except Exception as e:
        print(" Error during signup:", e)


def teacher_login():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        tid = input("Teacher ID: ")
        pwd = input("Password: ")
        cursor.execute("SELECT * FROM teachers WHERE id=%s AND password=%s", (tid, pwd))
        teacher = cursor.fetchone()
        conn.close()
        if teacher:
            if teacher['status'] != 'Approved':
                print(f"Your account status is '{teacher['status']}'")
                return None
            print(f"Welcome Teacher {teacher['name']}!")
            return teacher['id']
        else:
            print("Invalid credentials")
            return None
    except Exception as e:
        print("Error during teacher login:", e)
        return None

# ----------------- STUDENT -----------------
def student_signup():
    try:
        print("\n--- Student Sign Up ---")
        roll_no = input("Enter Roll No: ")
        name = input("Enter Name: ")
        branch = input("Enter Branch: ")
        email = input("Enter Email: ")
        password = input("Enter Password: ")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE roll_no=%s", (roll_no,))
        if cursor.fetchone():
            print("Student already exists!")
            conn.close()
            return None

        cursor.execute(
            "INSERT INTO students(roll_no, name, branch, email, password) VALUES(%s,%s,%s,%s,%s)",
            (roll_no, name, branch, email, password)
        )
        conn.commit()
        conn.close()
        print("Student registered successfully!")
        return True
    except Exception as e:
        print("Error during student signup:", e)


def student_login():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        roll_no = input("Student Roll No: ").strip()
        pwd = input("Password: ").strip()

        if not roll_no or not pwd:
            print("Roll No and Password cannot be empty!")
            return None

        cursor.execute("SELECT * FROM students WHERE roll_no=%s AND password=%s", (roll_no, pwd))
        student = cursor.fetchone()
        conn.close()

        if student:
            print(f"Welcome Student {student['name']}!")
            print("Your Attendance Report:")
            view_attendance_by_student(student['roll_no'])
            return student['roll_no']
        else:
            print("Invalid credentials")
            return None
    except Exception as e:
        print("Error during student login:", e)
        return None

# ----------------- ADMIN -----------------
def admin_login():
    try:
        user = input("Admin Username: ")
        pwd = input("Admin Password: ")
        if user == "devanshu" and pwd == "devanshu123":
            print("Admin logged in!")
            return True
        else:
            print("Invalid admin credentials")
            return False
    except Exception as e:
        print("Admin login error:", e)
        return False


def admin_approve_teacher():
    try:
        if not admin_login():
            return
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id,name,email FROM teachers WHERE status='Pending'")
        pending = cursor.fetchall()
        if not pending:
            print("No pending teachers.")
            conn.close()
            return
        print("\n--- Pending Teachers ---")
        for t in pending:
            print(f"ID: {t['id']} | Name: {t['name']} | Email: {t['email']}")

        while True:
            choice = input("Enter Teacher ID to Approve/Reject (or 'q' to quit): ")
            if choice.lower() == 'q':
                break
            action = input("Approve (A) / Reject (R): ").upper()
            if action == 'A':
                cursor.execute("UPDATE teachers SET status='Approved' WHERE id=%s", (choice,))
                print(f"Teacher ID {choice} approved!")
            elif action == 'R':
                cursor.execute("UPDATE teachers SET status='Rejected' WHERE id=%s", (choice,))
                print(f"Teacher ID {choice} rejected!")
            else:
                print("Invalid action")
            conn.commit()
        conn.close()
    except Exception as e:
        print("Error during admin approval:", e)


