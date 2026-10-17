from teacher import teacher_menu
from student import student_menu
from subject import subject_menu

# Main Menu
while True:
    print("\n=== Attendance System ===")
    print("1. Teacher Management")
    print("2. Student Management")
    print("3. Subject Management")
    print("4. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        teacher_menu()
    elif choice == "2":
        student_menu()
    elif choice == "3":
        subject_menu()
    elif choice == "4":
        print("Exiting...")
        break
    else:
        print("Invalid Choice")
