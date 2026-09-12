from datetime import datetime
import os
import struct

STUDENT_FILE = "students.dat"
COURSE_FILE = "courses.dat"
ENROLLMENT_FILE = "enrollments.dat"
REPORT_FILE = "registration_report.txt"

STUDENT_STRUCT = struct.Struct("<20s50s30si?1s")
COURSE_STRUCT = struct.Struct("<20s50sI?1s")
ENROLLMENT_STRUCT = struct.Struct("<20s20s?")


def pack_string(s: str, length: int) -> bytes:
    return s.strip().encode("utf-8")[:length].ljust(length, b"\x00")


def unpack_string(b: bytes) -> str:
    return b.decode("utf-8", errors="ignore").rstrip("\x00").strip()


def read_file(filename: str, struct_def: struct.Struct) -> list:
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

def write_file(filename: str, struct_def: struct.Struct, records: list):
    with open(filename, "wb") as f:
        for rec in records:
            f.write(struct_def.pack(*rec))
        f.flush()
        os.fsync(f.fileno())

def append_record(filename: str, struct_def: struct.Struct, record: tuple):
    with open(filename, "ab") as f:
        f.write(struct_def.pack(*record))
        f.flush()
        os.fsync(f.fileno())

def add_student():
    print("\n--- เพิ่มนักศึกษาใหม่ ---")
    student_id = input("รหัสนักศึกษา: ").strip()
    name = input("ชื่อ-นามสกุล: ").strip()
    faculty = input("คณะ: ").strip()
    try:
        year = int(input("ปีการศึกษา: "))
    except ValueError:
        print(" ปีการศึกษาต้องเป็นตัวเลข")
        return

    record = (
        pack_string(student_id, 20),
        pack_string(name, 50),
        pack_string(faculty, 30),
        year,
        True,
        b"\x00",
    )
    append_record(STUDENT_FILE, STUDENT_STRUCT, record)
    print(" เพิ่มข้อมูลนักศึกษาเรียบร้อย")

def add_course():
    print("\n--- เพิ่มรายวิชาใหม่ ---")
    course_id = input("รหัสวิชา: ").strip()
    name = input("ชื่อวิชา: ").strip()
    try:
        credits = int(input("หน่วยกิต: "))
    except ValueError:
        print(" หน่วยกิตต้องเป็นตัวเลข")
        return

    record = (
        pack_string(course_id, 20),
        pack_string(name, 50),
        credits,
        True,
        b"\x00",
    )
    append_record(COURSE_FILE, COURSE_STRUCT, record)
    print(" เพิ่มข้อมูลรายวิชาเรียบร้อย")

def add_enrollment():
    print("\n--- ลงทะเบียนเรียน ---")
    student_id = input("รหัสนักศึกษา: ").strip()
    course_id = input("รหัสวิชา: ").strip()
    record = (
        pack_string(student_id, 20),
        pack_string(course_id, 20),
        True,
    )
    append_record(ENROLLMENT_FILE, ENROLLMENT_STRUCT, record)
    print(" ลงทะเบียนเรียบร้อย")

def menu_add():
    while True:
        print("\n=== 1) Add (เพิ่มข้อมูล) ===")
        print("1. เพิ่มนักศึกษา")
        print("2. เพิ่มรายวิชา")
        print("3. เพิ่มการลงทะเบียน")
        print("0. ย้อนกลับ")
        choice = input("เลือกเมนูย่อย: ").strip()
        if choice == "1":
            add_student()
        elif choice == "2":
            add_course()
        elif choice == "3":
            add_enrollment()
        elif choice == "0":
            break

def update_student():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    student_id = input("กรอกรหัสนักศึกษาที่ต้องการแก้ไข: ").strip()
    for i, s in enumerate(students):
        if unpack_string(s[0]) == student_id and s[4]:  
            curr_name = unpack_string(s[1])
            curr_fac = unpack_string(s[2])
            name = input(f"ชื่อใหม่ ({curr_name}): ").strip() or curr_name
            faculty = input(f"คณะใหม่ ({curr_fac}): ").strip() or curr_fac
            year_in = input(f"ปีใหม่ ({s[3]}): ").strip()
            year = int(year_in) if year_in else s[3]

            students[i] = (
                pack_string(student_id, 20),
                pack_string(name, 50),
                pack_string(faculty, 30),
                year,
                s[4],
                s[5],
            )
            write_file(STUDENT_FILE, STUDENT_STRUCT, students)
            print(" แก้ไขข้อมูลนักศึกษาเรียบร้อย")
            return
    print(" ไม่พบรหัสนักศึกษานี้ หรือ ข้อมูลถูกลบไปแล้ว")

def update_course():
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    course_id = input("กรอกรหัสวิชาที่ต้องการแก้ไข: ").strip()
    for i, c in enumerate(courses):
        if unpack_string(c[0]) == course_id and c[3]:
            curr_name = unpack_string(c[1])
            name = input(f"ชื่อใหม่ ({curr_name}): ").strip() or curr_name
            cred_in = input(f"หน่วยกิตใหม่ ({c[2]}): ").strip()
            credits = int(cred_in) if cred_in else c[2]
            courses[i] = (
                pack_string(course_id, 20),
                pack_string(name, 50),
                credits,
                c[3],
                c[4],
            )
            write_file(COURSE_FILE, COURSE_STRUCT, courses)
            print(" แก้ไขข้อมูลรายวิชาเรียบร้อย")
            return
    print(" ไม่พบรหัสวิชานี้ หรือ ข้อมูลถูกลบไปแล้ว")

def menu_update():
    while True:
        print("\n=== 2) Update (แก้ไขข้อมูล) ===")
        print("1. แก้ไขข้อมูลนักศึกษา")
        print("2. แก้ไขข้อมูลรายวิชา")
        print("0. ย้อนกลับ")
        choice = input("เลือกเมนูย่อย: ").strip()
        if choice == "1":
            update_student()
        elif choice == "2":
            update_course()
        elif choice == "0":
            break

def delete_student():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    student_id = input("กรอกรหัสนักศึกษาที่ต้องการลบ: ").strip()
    for i, s in enumerate(students):
        if unpack_string(s[0]) == student_id and s[4]:
            students[i] = (s[0], s[1], s[2], s[3], False, s[5])
            write_file(STUDENT_FILE, STUDENT_STRUCT, students)
            print(" ลบรหัสนักศึกษานี้เรียบร้อย ")
            return
    print(" ไม่พบรหัสนักศึกษานี้")

def delete_course():
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    course_id = input("กรอกรหัสวิชาที่ต้องการลบ: ").strip()
    for i, c in enumerate(courses):
        if unpack_string(c[0]) == course_id and c[3]:
            courses[i] = (c[0], c[1], c[2], False, c[4])
            write_file(COURSE_FILE, COURSE_STRUCT, courses)
            print(" ลบรายวิชาเรียบร้อย ")
            return
    print(" ไม่พบรหัสรายวิชานี้")

def drop_enrollment():
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    student_id = input("รหัสนักศึกษา: ").strip()
    course_id = input("รหัสวิชา: ").strip()

    for i, e in enumerate(enrollments):
        if (
            unpack_string(e[0]) == student_id
            and unpack_string(e[1]) == course_id
        ):
            if not e[2]:
                print(" รายการนี้ถูกถอนไปแล้ว")
                return
            enrollments[i] = (e[0], e[1], False)
            write_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT, enrollments)
            print(" ถอนการลงทะเบียนเรียบร้อย")
            return
    print(" ไม่พบรายการลงทะเบียนนี้")

def menu_delete():
    while True:
        print("\n=== 3) Delete (ลบ/ถอนรายการ) ===")
        print("1. ลบนักศึกษา")
        print("2. ลบรายวิชา")
        print("3. ถอนการลงทะเบียน (Drop)")
        print("0. ย้อนกลับ")
        choice = input("เลือกเมนูย่อย: ").strip()
        if choice == "1":
            delete_student()
        elif choice == "2":
            delete_course()
        elif choice == "3":
            drop_enrollment()
        elif choice == "0":
            break

def view_single_student():
    student_id = input("กรอกรหัสนักศึกษาที่ต้องการค้นหา: ").strip()
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    for s in students:
        if unpack_string(s[0]) == student_id:
            status = "Active" if s[4] else "Deleted"
            print(
                f"\n[ผลการค้นหา] ID: {unpack_string(s[0])} | Name: {unpack_string(s[1])} | Faculty: {unpack_string(s[2])} | Year: {s[3]} | Status: {status}"
            )
            return
    print(" ไม่พบข้อมูลนักศึกษา")

def view_all():
    print("\n--- รายชื่อนักศึกษาทั้งหมด ---")
    for s in read_file(STUDENT_FILE, STUDENT_STRUCT):
        print(
            f"ID: {unpack_string(s[0])}, Name: {unpack_string(s[1])}, Faculty: {unpack_string(s[2])}, Year: {s[3]}, Status: {'Active' if s[4] else 'Deleted'}"
        )

    print("\n--- รายวิชาทั้งหมด ---")
    for c in read_file(COURSE_FILE, COURSE_STRUCT):
        print(
            f"ID: {unpack_string(c[0])}, Name: {unpack_string(c[1])}, Credits: {c[2]}, Status: {'Active' if c[3] else 'Deleted'}"
        )

    print("\n--- การลงทะเบียนทั้งหมด ---")
    for e in read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT):
        print(
            f"Student ID: {unpack_string(e[0])}, Course ID: {unpack_string(e[1])}, Status: {'Active' if e[2] else 'Dropped'}"
        )

def view_filtered_enrollments():
    student_id = input("กรอกรหัสนักศึกษาเพื่อดูรายวิชาที่ลงทะเบียน: ").strip()
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    filtered = [e for e in enrollments if unpack_string(e[0]) == student_id]
    print(f"\n--- ประวัติการลงทะเบียนของรหัส {student_id} ---")
    if not filtered:
        print("ไม่พบรายการลงทะเบียน")
        return
    for e in filtered:
        status = "Active" if e[2] else "Dropped"
        print(f"Course ID: {unpack_string(e[1])} | Status: {status}")

def view_summary_stats():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)

    active_students = sum(1 for s in students if s[4])
    active_courses = sum(1 for c in courses if c[3])
    active_enrolls = sum(1 for e in enrollments if e[2])

    print("\n=== สถิติโดยสรุป ===")
    print(f"- นักศึกษาทั้งหมด (Active): {active_students}")
    print(f"- รายวิชาทั้งหมด (Active)  : {active_courses}")
    print(f"- การลงทะเบียน (Active)   : {active_enrolls}")
    print(f"- การถอนเรียน (Dropped)   : {len(enrollments) - active_enrolls}")

def menu_view():
    while True:
        print("\n=== 4) View (ดูข้อมูล) ===")
        print("1. ดูรายการเดียว (ค้นหานักศึกษา)")
        print("2. ดูทั้งหมด")
        print("3. ดูแบบกรอง (การลงทะเบียนรายบุคคล)")
        print("4. สถิติโดยสรุป")
        print("0. ย้อนกลับ")
        choice = input("เลือกเมนูย่อย: ").strip()
        if choice == "1":
            view_single_student()
        elif choice == "2":
            view_all()
        elif choice == "3":
            view_filtered_enrollments()
        elif choice == "4":
            view_summary_stats()
        elif choice == "0":
            break

def generate_report():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    col_widths = [15, 12, 8, 5, 10, 25, 7, 8]
    headers = [
        "Stud.ID",
        "Name",
        "Faculty",
        "Year",
        "Course ID",
        "Course Name",
        "Credits",
        "Status",
    ]

    def line():
        return "+" + "+".join("-" * w for w in col_widths) + "+"

    def row(values):
        return (
            "|"
            + "|".join(str(v).ljust(w) for v, w in zip(values, col_widths))
            + "|"
        )

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("Registration System - Summary Report\n")
        f.write(f"Generated At : {now}\n")
        f.write("App Version : 1.0\n")
        f.write("Encoding    : UTF-8 (fixed-length)\n\n")
        f.write(line() + "\n")
        f.write(row(headers) + "\n")
        f.write(line() + "\n")

        for s in students:
            stud_id = unpack_string(s[0])
            name = unpack_string(s[1])
            faculty = unpack_string(s[2])
            year = s[3]

            stud_enroll = [
                e for e in enrollments if unpack_string(e[0]) == stud_id
            ]

            if stud_enroll:
                has_rows = False
                for e in stud_enroll:
                    course_id = unpack_string(e[1])
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
                    status = "Enrolled" if e[2] else "Dropped"

                    if not has_rows:
                        f.write(
                            row([
                                stud_id,
                                name,
                                faculty,
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
                                course_id,
                                course_name,
                                credits,
                                status,
                            ])
                            + "\n"
                        )
            else:
                f.write(
                    row([stud_id, name, faculty, year, "", "", "", ""]) + "\n"
                )

            f.write(line() + "\n")

        f.write("\n")

        total_students = sum(1 for s in students if s[4])
        total_courses = sum(1 for c in courses if c[3])
        total_enrollment = len(enrollments)
        active_enrollments = sum(1 for e in enrollments if e[2])
        dropped_enrollments = total_enrollment - active_enrollments

        f.write("Summary (เฉพาะ Active)\n")
        f.write(f"- Total Students   : {total_students}\n")
        f.write(f"- Total Courses    : {total_courses}\n")
        f.write(f"- Total Enrollments : {total_enrollment}\n")
        f.write(f"- Active Enrollments: {active_enrollments}\n")
        f.write(f"- Dropped Enrollments: {dropped_enrollments}\n\n")

        faculty_counts = {}
        for e in enrollments:
            stud_id = unpack_string(e[0])
            student = next(
                (
                    s
                    for s in students
                    if unpack_string(s[0]) == stud_id and s[4]
                ),
                None,
            )
            if student and e[2]:
                fac = unpack_string(student[2])
                faculty_counts[fac] = faculty_counts.get(fac, 0) + 1

        f.write("Courses by Faculty (Active only)\n")
        for fac, count in faculty_counts.items():
            f.write(f"- {fac:<8} : {count}\n")

    print(f" สร้างรายงานสำเร็จ: {REPORT_FILE}")

def main_menu():
    while True:
        print("\n==========================================")
        print("  ระบบลงทะเบียนเรียน ")
        print("==========================================")
        print("1) Add (เพิ่มข้อมูล)")
        print("2) Update (แก้ไขข้อมูล)")
        print("3) Delete (ลบ/ถอนรายการ)")
        print("4) View (ดูข้อมูล)")
        print("5) Generate Report") 
        print("0) Exit (ออก)")

        choice = input("เลือกเมนู (0-5): ").strip()
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
            print("\n Logged out successfully.")
            break
        else:
            print(" กรุณาเลือกตัวเลือก 0-5 เท่านั้น")

if __name__ == "__main__":
    main_menu()
