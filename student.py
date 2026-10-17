from db_connect import get_connection

def add_student(roll_no,name,branch,email,password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students(roll_no,name,branch,email,password) VALUES(%s,%s,%s,%s,%s)",
                       (roll_no,name,branch,email,password))
        conn.commit()
        conn.close()
        print("Student added!")
    except Exception as e:
        print("Add student error:", e)

def view_students():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        conn.close()
        for r in rows: print(r)
    except Exception as e:
        print("View student error:", e)

def student_menu():
    while True:
        print("\n--- Student Menu ---")
        print("1. Add Student")
        print("2. View Students")
        print("3. Exit")
        choice = input("Choice: ")
        if choice=="1":
            roll_no=input("Roll No: ")
            name=input("Name: ")
            branch=input("Branch: ")
            email=input("Email: ")
            password=input("Password: ")
            add_student(roll_no,name,branch,email,password)
        elif choice=="2": view_students()
        elif choice=="3": break
        else: print("Invalid Choice")
