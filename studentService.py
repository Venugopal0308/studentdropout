from flask import Flask, request, render_template, session
import mysql.connector

DB_HOST = "127.0.0.1"
DB_USER = "developer"
DB_PASSWORD = "1234"
DB_DATABASE = "project"


def initialize_db():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE
    )


def render_add_student():
    return render_template("add_student.html")


def add_student(student_data):
    student_name = student_data.get("student_name")
    reason = student_data.get("reason")
    year = student_data.get("year")
    attendance = student_data.get("attendance")
    address = student_data.get("address")
    aadhar_number = student_data.get("aadhar_number")
    contact = student_data.get("contact")
    schoolname = student_data.get("schools")
    Email = session.get("email")
    mydb = initialize_db()
    cursor = mydb.cursor()

    cursor.execute("SELECT id FROM school WHERE name=%s", (schoolname,))
    school_id = cursor.fetchone()[0]
    print(f"school id={school_id}")
    cursor.execute("SELECT id FROM person WHERE email=%s", (Email,))
    added_by_id = cursor.fetchone()[0]
    print(added_by_id)

    if not added_by_id:
        return render_template("login.html", message="Please log in first")

    else:
        sql = "INSERT INTO student (name, reason, year_of_dropout, attendance, address, school_id, aadhar_number, contact, added_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            student_name,
            reason,
            year,
            attendance,
            address,
            school_id,
            aadhar_number,
            contact,
            added_by_id,
        )

        cursor.execute(sql, values)
        mydb.commit()
        cursor.close()
        mydb.close()
        return render_template("studentdata", "Student data added successfully!")
