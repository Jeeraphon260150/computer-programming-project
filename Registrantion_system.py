import struct
import os
from datetime import datetime

STUDENT_FILE = "students.dat"
COURSE_FILE = "courses.dat"
ENROLLMENT_FILE = "enrollments.dat"
REPORT_FILE = "report.txt"
STUDENT_STRUCT = struct.Struct("20s50s30si?")   
COURSE_STRUCT = struct.Struct("20s50sI?")       
ENROLLMENT_STRUCT = struct.Struct("20s20s?")   

def pack_string(s, length):
    return s.strip().encode("utf-8")[:length].ljust(length, b"\x00")

def unpack_string(b):
    return b.decode("utf-8").rstrip("\x00").strip()

def read_file(filename, struct_def):
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

def write_file(filename, struct_def, records):
    with open(filename, "wb") as f:
        for rec in records:
            f.write(struct_def.pack(*rec))

def add_student():
    student_id = input("รหัสนักศึกษา: ").strip()
    name = input("ชื่อ: ").strip()
    faculty = input("คณะ: ").strip()
    year = int(input("ปี: "))
    active = True
    record = (pack_string(student_id,20), pack_string(name,50), pack_string(faculty,30), year, active)
    with open(STUDENT_FILE, "ab") as f:
        f.write(STUDENT_STRUCT.pack(*record))
    print("เพิ่มนักศึกษาเรียบร้อย")

def view_students():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    print("\n--- รายชื่อนักเรียน ---")
    for s in students:
        print(f"ID: {unpack_string(s[0])}, Name: {unpack_string(s[1])}, Faculty: {unpack_string(s[2])}, Year: {s[3]}, Status: {'Active' if s[4] else 'Deleted'}")

def update_student():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    student_id = input("กรอกรหัสนักศึกษาที่ต้องการแก้ไข: ").strip()
    for i, s in enumerate(students):
        if unpack_string(s[0]) == student_id:
            student_id = input(f"รหัสนักศึกษาใหม่ ({unpack_string(s[1])}): ").strip() or unpack_string(s[1])
            name = input(f"ชื่อใหม่ ({unpack_string(s[1])}): ").strip() or unpack_string(s[1])
            faculty = input(f"คณะใหม่ ({unpack_string(s[2])}): ").strip() or unpack_string(s[2])
            year = input(f"ปีใหม่ ({s[3]}): ").strip() or s[3]
            year = int(year)
            students[i] = (pack_string(student_id,20), pack_string(name,50), pack_string(faculty,30), year, s[4])
            write_file(STUDENT_FILE, STUDENT_STRUCT, students)
            print("แก้ไขเรียบร้อย")
            return
    print("ไม่พบรหัสนักศึกษานี้")

def delete_student():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    student_id = input("กรอกรหัสนักศึกษาที่ต้องการลบ: ").strip()
    for i, s in enumerate(students):
        if unpack_string(s[0]) == student_id:
            students[i] = (s[0], s[1], s[2], s[3], False)
            write_file(STUDENT_FILE, STUDENT_STRUCT, students)
            print("ลบเรียบร้อย (mark deleted)")
            return
    print("ไม่พบรหัสนักศึกษานี้")

def add_course():
    course_id = input("รหัสวิชา: ").strip()
    name = input("ชื่อวิชา: ").strip()
    credits = int(input("หน่วยกิต: "))
    active = True
    record = (pack_string(course_id,20), pack_string(name,50), credits, active)
    with open(COURSE_FILE, "ab") as f:
        f.write(COURSE_STRUCT.pack(*record))
    print("เพิ่มวิชาเรียบร้อย")

def view_courses():
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    print("\n--- รายวิชา ---")
    for c in courses:
        print(f"ID: {unpack_string(c[0])}, Name: {unpack_string(c[1])}, Credits: {c[2]}, Status: {'Active' if c[3] else 'Deleted'}")

def update_course():
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    course_id = input("กรอกรหัสวิชาที่ต้องการแก้ไข: ").strip()
    for i, c in enumerate(courses):
        if unpack_string(c[0]) == course_id:
            name = input(f"ชื่อใหม่ ({unpack_string(c[1])}): ").strip() or unpack_string(c[1])
            credits = input(f"หน่วยกิตใหม่ ({c[2]}): ").strip() or c[2]
            credits = int(credits)
            courses[i] = (pack_string(course_id,20), pack_string(name,50), credits, c[3])
            write_file(COURSE_FILE, COURSE_STRUCT, courses)
            print("แก้ไขเรียบร้อย")
            return
    print("ไม่พบรหัสวิชานี้")

def delete_course():
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    course_id = input("กรอกรหัสวิชาที่ต้องการลบ: ").strip()
    for i, c in enumerate(courses):
        if unpack_string(c[0]) == course_id:
            courses[i] = (c[0], c[1], c[2], False)
            write_file(COURSE_FILE, COURSE_STRUCT, courses)
            print("ลบเรียบร้อย (mark deleted)")
            return
    print("ไม่พบรหัสวิชานี้")

def add_enrollment():
    student_id = input("รหัสนักศึกษา: ").strip()
    course_id = input("รหัสวิชา: ").strip()
    active = True
    record = (pack_string(student_id,20), pack_string(course_id,20), active)
    with open(ENROLLMENT_FILE, "ab") as f:
        f.write(ENROLLMENT_STRUCT.pack(*record))
    print("เพิ่มการลงทะเบียนเรียบร้อย")

def view_enrollments():
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    print("\n--- การลงทะเบียน ---")
    for e in enrollments:
        print(f"Student ID: {unpack_string(e[0])}, Course ID: {unpack_string(e[1])}, Status: {'Active' if e[2] else 'Deleted'}")

def update_enrollment():
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    student_id = input("รหัสนักศึกษา: ").strip()
    course_id = input("รหัสวิชา: ").strip()
    for i, e in enumerate(enrollments):
        if unpack_string(e[0]) == student_id and unpack_string(e[1]) == course_id:
            new_course = input(f"รหัสวิชาใหม่ ({unpack_string(e[1])}): ").strip() or unpack_string(e[1])
            enrollments[i] = (e[0], pack_string(new_course,20), e[2])
            write_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT, enrollments)
            print("แก้ไขเรียบร้อย")
            return
    print("ไม่พบการลงทะเบียนนี้")

def delete_enrollment():
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    student_id = input("รหัสนักศึกษา: ").strip()
    course_id = input("รหัสวิชา: ").strip()
    for i, e in enumerate(enrollments):
        if unpack_string(e[0]) == student_id and unpack_string(e[1]) == course_id:
            enrollments[i] = (e[0], e[1], False)
            write_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT, enrollments)
            print("ลบการลงทะเบียนเรียบร้อย (mark deleted)")
            return
    print("ไม่พบการลงทะเบียนนี้")   

def drop_enrollment():
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    student_id = input("รหัสนักศึกษา: ").strip()
    course_id = input("รหัสวิชา: ").strip()

    for i, e in enumerate(enrollments):
        if unpack_string(e[0]) == student_id and unpack_string(e[1]) == course_id:
            if not e[2]:
                print("การลงทะเบียนนี้ถูกถอนแล้ว")
                return
            enrollments[i] = (e[0], e[1], False)
            write_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT, enrollments)
            print("ถอนการลงทะเบียนเรียบร้อย")
            return

    print("ไม่พบการลงทะเบียนนี้")

def generate_report():
    students = read_file(STUDENT_FILE, STUDENT_STRUCT)
    courses = read_file(COURSE_FILE, COURSE_STRUCT)
    enrollments = read_file(ENROLLMENT_FILE, ENROLLMENT_STRUCT)
    
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    col_widths = [15, 20, 12, 4, 12, 25, 7, 8]
    headers = ["Stud.ID", "Name", "Faculty", "Year", "Course ID", "Course Name", "Credits", "Status"]

    def line():
        return "+" + "+".join("-" * w for w in col_widths) + "+"

    def row(values):
        return "|" + "|".join(str(v).ljust(w) for v, w in zip(values, col_widths)) + "|"

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("Registration System – Summary Report\n")
        f.write(f"Generated At : {now}\n")
        f.write("App Version  : 1.0\n")
        f.write("Encoding     : UTF-8 (fixed-length)\n\n")

        f.write(line() + "\n")
        f.write(row(headers) + "\n")
        f.write(line() + "\n")

        for s in students:
            stud_id = unpack_string(s[0])
            name = unpack_string(s[1])
            faculty = unpack_string(s[2])
            year = s[3]

            stud_enroll = [e for e in enrollments if unpack_string(e[0]) == stud_id]

            if stud_enroll:
                has_rows = False
                for i, e in enumerate(stud_enroll):
                    course_id = unpack_string(e[1])
                    course = next((c for c in courses if unpack_string(c[0]) == course_id), None)
                    
                    course_name = unpack_string(course[1]) if course else "Unknown Course"
                    credits = course[2] if course else 0
                    status = "Enrolled" if e[2] else "Dropped"
                    
                    if not has_rows:
                        f.write(row([stud_id, name, faculty, year, course_id, course_name, credits, status]) + "\n")
                        has_rows = True
                    else:
                        f.write(row(["", "", "", "", course_id, course_name, credits, status]) + "\n")
            else:
                f.write(row([stud_id, name, faculty, year, "", "", "", ""]) + "\n")
            
            f.write(line() + "\n")

        f.write("\n")
        
        total_students = sum(1 for s in students if s[4])
        total_courses = sum(1 for c in courses if c[3])
        total_enrollment = len(enrollments)
        active_enrollments = sum(1 for e in enrollments if e[2])
        dropped_enrollments = total_enrollment - active_enrollments

        f.write("Summary (เฉพาะ Active)\n")
        f.write(f"- Total Students      : {total_students}\n")
        f.write(f"- Total Courses       : {total_courses}\n")
        f.write(f"- Total Enrollments   : {total_enrollment}\n")
        f.write(f"- Active Enrollments  : {active_enrollments}\n")
        f.write(f"- Dropped Enrollments : {dropped_enrollments}\n\n")

        faculty_counts = {}
        for e in enrollments:
            stud_id = unpack_string(e[0])
            student = next((s for s in students if unpack_string(s[0]) == stud_id and s[4]), None)
            if student:
                fac = unpack_string(student[2])
                faculty_counts[fac] = faculty_counts.get(fac, 0) + 1

        f.write("Courses by Faculty (Active only)\n")
        for fac, count in faculty_counts.items():
            f.write(f"- {fac:<11}: {count}\n")

    print(f"สร้างรายงานเรียบร้อย: {REPORT_FILE}")

def main_menu():
    while True:
        print("\n=== ระบบลงทะเบียนเรียน ===")
        print("1) Add Student")
        print("2) Update Student")
        print("3) Delete Student")
        print("4) View Students")
        print("5) Add Course")
        print("6) Update Course")
        print("7) Delete Course")
        print("8) View Courses")
        print("9) Add Enrollment")
        print("10) View Enrollments")
        print("11) Update Enrollment")
        print("12) Delete Enrollment")
        print("13) Drop Enrollment")   
        print("14) Generate Report")
        print("15) Exit")

        choice = input("เลือกเมนู (1-15): ").strip()
        if choice == "1": add_student() #เพิ่มข้อมูลนักศึกษาใหม่ลงระบบ
        elif choice == "2": update_student() #แก้ไขข้อมูลนักศึกษาที่มีอยู่แล้ว
        elif choice == "3": delete_student() #ลบนักศึกษาออกจากระบบ
        elif choice == "4": view_students() #แสดงรายชื่อนักศึกษาทั้งหมดในระบบ
        elif choice == "5": add_course() #เพิ่มรายวิชาใหม่ลงระบบ
        elif choice == "6": update_course() #แก้ไขข้อมูลรายวิชา 
        elif choice == "7": delete_course() #ลบรายวิชาออกจากระบบ
        elif choice == "8": view_courses() #แสดงรายวิชาทั้งหมดในระบบ
        elif choice == "9": add_enrollment() #ผูกนักศึกษากับวิชาเรียน
        elif choice == "10": view_enrollments() #แสดงรายการลงทะเบียนทั้งหมด
        elif choice == "11": update_enrollment() #แก้ไขข้อมูลการลงทะเบียน
        elif choice == "12": delete_enrollment() #ลบรายการลงทะเบียน
        elif choice == "13": drop_enrollment() #ถอนรายวิชา  
        elif choice == "14": generate_report() #ประมวลผลและสร้างไฟล์รายงานสรุป
        elif choice == "15":
            print("ออกจากโปรแกรม")
            break
        else:
            print("กรุณาเลือกเมนู 1-15 เท่านั้น")

if __name__ == "__main__":
    main_menu()