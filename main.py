# main.py
from teacher import teacher_menu
from student import student_menu
from subject import subject_menu
from attendance import teacher_attendance_menu, student_attendance_menu
from login_signup import teacher_signup, teacher_login, student_signup, student_login, admin_approve_teacher

def login_signup_menu():
    while True:
        print("\n--- Login / Signup ---")
        print("1. Teacher Login")
        print("2. Teacher Signup")
        print("3. Student Login")
        print("4. Student Signup")
        print("5. Admin Approve Teachers")
        print("6. Back to Main Menu")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            tid = teacher_login()
            if tid:
                teacher_menu()

        elif choice == "2":
            teacher_signup()

        elif choice == "3":
            roll_no = student_login()
            if roll_no:
                student_menu()

        elif choice == "4":
            student_signup()

        elif choice == "5":
            # Admin approval directly from menu
            admin_approve_teacher()

        elif choice == "6":
            break

        else:
            print("Invalid choice, try again.")

def main_menu():
    while True:
        try:
            print("\n=== Attendance System ===")
            print("1. Login / Signup")
            print("2. Teacher Management")
            print("3. Student Management")
            print("4. Subject Management")
            print("5. Attendance System")
            print("6. Exit")

            choice = input("Enter choice: ").strip()

            if choice == "1":
                login_signup_menu()

            elif choice == "2":
                teacher_menu()

            elif choice == "3":
                student_menu()

            elif choice == "4":
                subject_menu()

            elif choice == "5":
                while True:
                    print("\n--- Attendance Menu ---")
                    print("1. Teacher Attendance")
                    print("2. Student Attendance")
                    print("3. Back")
                    att_choice = input("Enter choice: ").strip()

                    if att_choice == "1":
                        teacher_id = input("Enter your Teacher ID: ").strip()
                        if teacher_id.isdigit():
                            teacher_attendance_menu(int(teacher_id))
                        else:
                            print("Teacher ID must be a number")

                    elif att_choice == "2":
                        student_roll_no = input("Enter your Roll No: ").strip()
                        if student_roll_no != "":
                            student_attendance_menu(student_roll_no)
                        else:
                            print("Roll No cannot be empty")

                    elif att_choice == "3":
                        break

                    else:
                        print("Invalid choice, try again.")

            elif choice == "6":
                print("Exiting System... Goodbye!")
                break

            else:
                print("Invalid choice, try again.")

        except KeyboardInterrupt:
            print("\nProgram interrupted by user. Exiting...")
            break

        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main_menu()
