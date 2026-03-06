def read_file_to_dict(filename):
    student_dict = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    name, grade = line.split(",")
                    student_dict[name.strip()] = float(grade.strip())
                except ValueError:
                    print(f"Skipping invalid line: {line}")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return {}

def add_student(student_dict, name, grade):
    student_dict[name] = grade
    print(f"Student '{name}' added with grade {grade}.")

def calculate_average(student_dict):
    if not student_dict:
        print("No students found.")
        return None

    all_grades = student_dict.values()
    total_grades = sum(all_grades)
    average = total_grades / len(all_grades)
    print(f"Average grade: {average}")
    return average

def print_above_average_students(student_dict, average):
    if not student_dict:
        print("No students found.")
        return

    print("Students who scored above average:")
    for name, grade in student_dict.items():
        if grade > average:
            print(f"{name}: {grade}")
        else:
            print("No student scored above average")

# Main program
if __name__ == "__main__":
    filename = "students.txt"
    students = read_file_to_dict(filename)

    while True:
        print("\nOptions:")
        print("1. Add new student data")
        print("2. Calculate average grade")
        print("3. Print students who scored above average")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter student name: ")
            try:
                grade = float(input("Enter student grade: "))
                add_student(students, name, grade)
            except ValueError:
                print("Invalid grade. Please enter a number.")
        elif choice == "2":
           calculate_average(students)
        elif choice == "3":
            average = calculate_average(students)
            if average is not None:
                print_above_average_students(students, average)
        elif choice == "4":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
