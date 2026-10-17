from db_connect import get_connection

def add_subject(name,branch,teacher_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects(name,branch,teacher_id) VALUES(%s,%s,%s)",(name,branch,teacher_id))
        conn.commit()
        conn.close()
        print("Subject added!")
    except Exception as e:
        print("Add subject error:", e)

def view_subjects():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects")
        rows = cursor.fetchall()
        conn.close()
        for r in rows: print(r)
    except Exception as e:
        print("View subject error:", e)

def subject_menu():
    while True:
        print("\n--- Subject Menu ---")
        print("1. Add Subject")
        print("2. View Subjects")
        print("3. Exit")
        choice = input("Choice: ")
        if choice=="1":
            name=input("Name: ")
            branch=input("Branch: ")
            tid=input("Teacher ID: ")
            add_subject(name,branch,tid)
        elif choice=="2": view_subjects()
        elif choice=="3": break
        else: print("Invalid Choice")
