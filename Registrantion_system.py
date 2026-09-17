from datetime import datetime
import os
import struct
from typing import List, Tuple

STUDENT_FILE = "students.dat"
COURSE_FILE = "courses.dat"
ENROLLMENT_FILE = "enrollments.dat"
REPORT_FILE = "registration_report.txt"


STUDENT_STRUCT = struct.Struct("<q90s90s90si")
COURSE_STRUCT = struct.Struct("<20s90sI")
ENROLLMENT_STRUCT = struct.Struct("<q20s10s")


def pack_string(s: str, max_bytes: int) -> bytes:
    encoded = s.strip().encode("utf-8")
    if len(encoded) > max_bytes:
        encoded = (
            encoded[:max_bytes].decode("utf-8", errors="ignore").encode("utf-8")
        )
    return encoded.ljust(max_bytes, b"\x00")


def unpack_string(b: bytes) -> str:
    return b.decode("utf-8", errors="ignore").rstrip("\x00").strip()


def get_display_width(s: str) -> int:
    width = 0
    for char in s:
        code = ord(char)
        if 0x0E31 <= code <= 0x0E3A or 0x0E47 <= code <= 0x0E4E:
            continue
        elif (
            (0x0E00 <= code <= 0x0E7F)
            or (0x1100 <= code <= 0x11FF)
            or (0x2E80 <= code <= 0xA4CF)
        ):
            width += 2
        else:
            width += 1
    return width


def pad_str(s: str, width: int) -> str:
    s_str = str(s)
    current_w = get_display_width(s_str)
    padding = width - current_w
    return s_str + (" " * max(0, padding))


def read_file(filename: str, struct_def: struct.Struct) -> List[Tuple]:
    records = []
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(struct_def.size)
                if not chunk:
                    break
                if len(chunk) == struct_def.size:
                    records.append(struct_def.unpack(chunk))
    return records


def write_file(filename: str, struct_def: struct.Struct, records: List[Tuple]):
    with open(filename, "wb") as f:
        for rec in records:
            f.write(struct_def.pack(*rec))
        f.flush()
        os.fsync(f.fileno())


def append_record(
    filename: str, struct_def: struct.Struct, record: Tuple
) -> None:
    with open(filename, "ab") as f:
        f.write(struct_def.pack(*record))
        f.flush()
        os.fsync(f.fileno())


def add_student():
    print("\n --- Add Student Data ---")
    try:
        student_id = int(input("Student ID: ").strip())
    except ValueError:
        print("Student ID must be a number.")
        return

    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    for s in students:
        if s[0] == student_id:
            print("Student ID already exists in the system.")
            return

    name = input("Name: ").strip()
    faculty = input("Faculty: ").strip()
    dept = input("Department: ").strip()
    try:
        year = int(input("Year (number): "))
    except ValueError:
        print("Year must be a whole number.")
        return

    record = (
        student_id,
        pack_string(name, 90),
        pack_string(faculty, 90),
        pack_string(dept, 90),
        year,
    )
    append_record(STUDENT_FILE, STUDENT_STRUCT, record)
    print("Student data saved successfully.")


def add_course():
    print("\n --- Add Course Data ---")
    course_id = input("Course ID: ").strip()
    if not course_id:
        print("Course ID cannot be empty.")
        return

    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    for c in courses:
        if unpack_string(c[0]) == course_id:
            print("Course ID already exists in the system.")
            return

    name = input("Course Name: ").strip()
    try:
        credits = int(input("Credits (number): "))
    except ValueError:
        print("Credits must be a whole number.")
        return

    record = (
        pack_string(course_id, 20),
        pack_string(name, 90),
        credits,
    )
    append_record(COURSE_FILE, COURSE_STRUCT, record)
    print("Course data saved successfully.")


def add_enrollment():
    print("\n --- Add Course Enrollment ---")
    try:
        student_id = int(input("Student ID: ").strip())
    except ValueError:
        print("Student ID must be a number.")
        return

    course_id = input("Course ID: ").strip()
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)

    if not any(s[0] == student_id for s in students):
        print("Student ID not found in the system.")
        return
    if not any(unpack_string(c[0]) == course_id for c in courses):
        print("Course ID not found in the system.")
        return

    for e in enrollments:
        if e[0] == student_id and unpack_string(e[1]) == course_id:
            status = unpack_string(e[2])
            if status == "Enrolled":
                print("Student has already enrolled in this course.")
                return

    record = (
        student_id,
        pack_string(course_id, 20),
        pack_string("Enrolled", 10),
    )
    append_record(ENROLLMENT_FILE, ENROLLMENT_STRUCT, record)
    print("Enrollment data saved successfully.")


def menu_add():
    while True:
        print("\n==========================================")
        print("  1) Add Data Menu")
        print("==========================================")
        print("1. Add Student")
        print("2. Add Course")
        print("3. Add Enrollment")
        print("0. Back to Main Menu")
        choice = input("Select sub-menu [0-3]: ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            add_course()
        elif choice == "3":
            add_enrollment()
        elif choice == "0":
            break
        else:
            print("Invalid option. Please try again.")


def update_student():
    print("\n --- Update Student Data ---")
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    try:
        student_id = int(input("Enter Student ID to update: ").strip())
    except ValueError:
        print("Student ID must be a number.")
        return

    for i, s in enumerate(students):
        if s[0] == student_id:
            curr_name = unpack_string(s[1])
            curr_fac = unpack_string(s[2])
            curr_dept = unpack_string(s[3])
            print("(Press Enter to keep current value)")
            name = input(f"New Name [{curr_name}]: ").strip() or curr_name
            faculty = input(f"New Faculty [{curr_fac}]: ").strip() or curr_fac
            dept = input(f"New Department [{curr_dept}]: ").strip() or curr_dept
            year_in = input(f"New Year [{s[4]}]: ").strip()
            year = int(year_in) if year_in else s[4]

            students[i] = (
                student_id,
                pack_string(name, 90),
                pack_string(faculty, 90),
                pack_string(dept, 90),
                year,
            )
            write_file(STUDENT_FILE, STUDENT_STRUCT, students)
            print("Student data updated successfully.")
            return

    print("Student ID not found.")


def update_course():
    print("\n --- Update Course Data ---")
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    course_id = input("Enter Course ID to update: ").strip()

    for i, c in enumerate(courses):
        if unpack_string(c[0]) == course_id:
            curr_name = unpack_string(c[1])
            print("(Press Enter to keep current value)")
            name = (
                input(f"New Course Name [{curr_name}]: ").strip() or curr_name
            )
            cred_in = input(f"New Credits [{c[2]}]: ").strip()
            credits = int(cred_in) if cred_in else c[2]

            courses[i] = (
                pack_string(course_id, 20),
                pack_string(name, 90),
                credits,
            )
            write_file(COURSE_FILE, COURSE_STRUCT, courses)
            print("Course data updated successfully.")
            return

    print("Course ID not found.")


def menu_update():
    while True:
        print("\n==========================================")
        print("  2) Update Data Menu")
        print("==========================================")
        print("1. Update Student Data")
        print("2. Update Course Data")
        print("0. Back to Main Menu")
        choice = input("Select sub-menu [0-2]: ").strip()

        if choice == "1":
            update_student()
        elif choice == "2":
            update_course()
        elif choice == "0":
            break
        else:
            print("Invalid option. Please try again.")


def delete_student():
    print("\n --- Permanently Delete Student Data ---")
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    try:
        student_id = int(input("Enter Student ID to delete: ").strip())
    except ValueError:
        print("Student ID must be a number.")
        return

    new_students = [s for s in students if s[0] != student_id]
    if len(new_students) < len(students):
        write_file(STUDENT_FILE, STUDENT_STRUCT, new_students)

        enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
        new_enrollments = [e for e in enrollments if e[0] != student_id]
        write_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT, new_enrollments)

        print("Student and associated enrollment data deleted successfully.")
    else:
        print("Student ID not found.")


def delete_course():
    print("\n --- Permanently Delete Course Data ---")
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    course_id = input("Enter Course ID to delete: ").strip()

    new_courses = [c for c in courses if unpack_string(c[0]) != course_id]
    if len(new_courses) < len(courses):
        write_file(COURSE_FILE, COURSE_STRUCT, new_courses)

        enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
        new_enrollments = [
            e for e in enrollments if unpack_string(e[1]) != course_id
        ]
        write_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT, new_enrollments)

        print("Course and associated enrollment data deleted successfully.")
    else:
        print("Course ID not found.")


def drop_enrollment():
    print("\n --- Drop Course (Change Status to Dropped) ---")
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    try:
        student_id = int(input("Student ID: ").strip())
    except ValueError:
        print("Student ID must be a number.")
        return
    course_id = input("Course ID: ").strip()

    updated = False
    for i, e in enumerate(enrollments):
        if e[0] == student_id and unpack_string(e[1]) == course_id:
            enrollments[i] = (
                student_id,
                pack_string(course_id, 20),
                pack_string("Dropped", 10),
            )
            updated = True
            break

    if updated:
        write_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT, enrollments)
        print("Course dropped successfully (Status changed to Dropped).")
    else:
        print("Enrollment record not found.")


def menu_delete():
    while True:
        print("\n==========================================")
        print("  3) Delete/Drop Management Menu")
        print("==========================================")
        print("1. Delete Student")
        print("2. Delete Course")
        print("3. Drop Enrollment")
        print("0. Back to Main Menu")
        choice = input("Select sub-menu [0-3]: ").strip()

        if choice == "1":
            delete_student()
        elif choice == "2":
            delete_course()
        elif choice == "3":
            drop_enrollment()
        elif choice == "0":
            break
        else:
            print("Invalid option. Please try again.")


def view_single():
    try:
        student_id = int(input("\nEnter Student ID to view data: ").strip())
    except ValueError:
        print("Student ID must be a number.")
        return

    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    for s in students:
        if s[0] == student_id:
            print("\n--- Student Details ---")
            print(f"Student ID : {s[0]}")
            print(f"Name       : {unpack_string(s[1])}")
            print(f"Faculty    : {unpack_string(s[2])}")
            print(f"Department : {unpack_string(s[3])}")
            print(f"Year       : {s[4]}")
            return
    print("Student data not found.")


def view_all():
    print("\n================ All Students ================")
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    for s in students:
        print(
            f"ID: {s[0]:<15} | Name: {unpack_string(s[1]):<30} | Faculty: {unpack_string(s[2]):<10} | Dept: {unpack_string(s[3]):<10} | Year: {s[4]}"
        )

    print("\n================ All Courses ================")
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    for c in courses:
        print(
            f"ID: {unpack_string(c[0]):<12} | Name: {unpack_string(c[1]):<30} | Credits: {c[2]}"
        )

    print("\n================ All Enrollments ================")
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    for e in enrollments:
        status = unpack_string(e[2]) if len(e) > 2 else "Enrolled"
        print(
            f"Student ID: {e[0]:<15} | Course ID: {unpack_string(e[1]):<12} | Status: {status}"
        )


def view_filtered():
    try:
        student_id = int(
            input("\nEnter Student ID to view filtered enrollments: ").strip()
        )
    except ValueError:
        print("Student ID must be a number.")
        return

    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    filtered = [e for e in enrollments if e[0] == student_id]

    print(f"\n--- Enrollment History for Student ID: {student_id} ---")
    if not filtered:
        print("No enrollment records found.")
        return
    for e in filtered:
        status = unpack_string(e[2]) if len(e) > 2 else "Enrolled"
        print(f"Course ID: {unpack_string(e[1]):<15} | Status: {status}")


def view_summary():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)

    print("\n================ Summary Statistics ================")
    print(f"- Total Students    : {len(students)}")
    print(f"- Total Courses     : {len(courses)}")
    print(f"- Total Enrollments : {len(enrollments)}")


def menu_view():
    while True:
        print("\n==========================================")
        print("  4) View Data Menu")
        print("==========================================")
        print("1. View Single Record (Search Student)")
        print("2. View All Records")
        print("3. View Filtered Records (by Student ID)")
        print("4. View Summary Statistics")
        print("0. Back to Main Menu")
        choice = input("Select sub-menu [0-4]: ").strip()

        if choice == "1":
            view_single()
        elif choice == "2":
            view_all()
        elif choice == "3":
            view_filtered()
        elif choice == "4":
            view_summary()
        elif choice == "0":
            break
        else:
            print("Invalid option. Please select [0-4].")


def generate_report():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    now_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    field_widths = [15, 28, 10, 12, 6, 12, 32, 9, 10]
    headers = [
        "Stud.ID",
        "Name",
        "Faculty",
        "Department",
        "Year",
        "Course ID",
        "Course Name",
        "Credits",
        "Status",
    ]

    def line():
        return "+" + "+".join("-" * (w + 2) for w in field_widths) + "+"

    def row(values):
        formatted_cells = []
        for v, w in zip(values, field_widths):
            formatted_cells.append(pad_str(str(v), w))
        return "| " + " | ".join(formatted_cells) + " |"

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("Registration System - Summary Report\n")
        f.write(f"Generated At : {now_str}\n")
        f.write("App Version : 1.0\n")
        f.write("Encoding    : UTF-8 (fixed-length)\n\n")
        f.write(line() + "\n")
        f.write(row(headers) + "\n")
        f.write(line() + "\n")

        for s in students:
            stud_id = s[0]
            name = unpack_string(s[1])
            faculty = unpack_string(s[2])
            dept = unpack_string(s[3])
            year = s[4]

            stud_enroll = [e for e in enrollments if e[0] == stud_id]

            if stud_enroll:
                has_rows = False
                for e in stud_enroll:
                    course_id = unpack_string(e[1])
                    status = (
                        unpack_string(e[2]) if len(e) > 2 else "Enrolled"
                    )

                    course = next(
                        (
                            c
                            for c in courses
                            if unpack_string(c[0]) == course_id
                        ),
                        None,
                    )

                    course_name = (
                        unpack_string(course[1])
                        if course
                        else "Unknown Course"
                    )
                    credits = course[2] if course else 0

                    if not has_rows:
                        f.write(
                            row([
                                stud_id,
                                name,
                                faculty,
                                dept,
                                year,
                                course_id,
                                course_name,
                                credits,
                                status,
                            ])
                            + "\n"
                        )
                        has_rows = True
                    else:
                        f.write(
                            row([
                                "",
                                "",
                                "",
                                "",
                                "",
                                course_id,
                                course_name,
                                credits,
                                status,
                            ])
                            + "\n"
                        )
            else:
                f.write(
                    row([stud_id, name, faculty, dept, year, "", "", "", ""])
                    + "\n"
                )

            f.write(line() + "\n")

        f.write("\n")
        f.write("Summary\n")
        f.write(f"- Total Students    : {len(students)}\n")
        f.write(f"- Total Courses     : {len(courses)}\n")
        f.write(f"- Total Enrollments : {len(enrollments)}\n\n")

        faculty_counts = {}
        for e in enrollments:
            stud_id = e[0]
            student = next((s for s in students if s[0] == stud_id), None)
            if student:
                fac = unpack_string(student[2])
                faculty_counts[fac] = faculty_counts.get(fac, 0) + 1

        f.write("Courses by Faculty\n")
        for fac, count in faculty_counts.items():
            f.write(f"- {fac:<8} : {count}\n")

    print(f"\nSummary report generated successfully: {REPORT_FILE}")


def main():
    while True:
        print("\n==========================================")
        print("          Registration System             ")
        print("==========================================")
        print("1) Add ")
        print("2) Update ")
        print("3) Delete/Drop Management")
        print("4) View ")
        print("5) Generate Report")
        print("0) Exit Program")
        choice = input("Select an option [0-5]: ").strip()
        if choice == "1":
            menu_add()
        elif choice == "2":
            menu_update()
        elif choice == "3":
            menu_delete()
        elif choice == "4":
            menu_view()
        elif choice == "5":
            generate_report()
        elif choice == "0":
            print("\nThe program has been closed.")
            break
        else:
            print("Invalid option. Please enter a number between 0 and 5.")


if __name__ == "__main__":
    main()