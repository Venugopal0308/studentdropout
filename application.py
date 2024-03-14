from flask import Flask, request, redirect, url_for, render_template, session
import mysql.connector
from service import studentService

app = Flask(__name__)

# Database connection parameters
DB_HOST = "127.0.0.1"
DB_USER = "developer"
DB_PASSWORD = "1234"
DB_DATABASE = "project"


def initialize_db():
    return mysql.connector.connect(
        host="127.0.0.1", user="developer", password="1234", database="project"
    )


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        email = request.form.get("username")
        password = request.form.get("password")

        mydb = initialize_db()
        cursor = mydb.cursor()
        query = (
            "SELECT name,role_type_id FROM person WHERE email = %s AND password = %s"
        )
        cursor.execute(query, (email, password))
        f = cursor.fetchone()
        if f:
            # Add user's email to the session
            session["email"] = email
            return redirect(url_for("home"))
        else:
            error_message = "Invalid email or password. Please try again."
            return render_template("login.html", error="error_message")

    return render_template("home.html")


@app.route("/profile")
def profile():
    mydb = initialize_db()
    cursor = mydb.cursor()
    # Check if the user is logged in (email is in the session)
    if "email" in session:
        # Fetch user data based on the email from the session
        email = session["email"]
        cursor.execute(
            "SELECT email,name,role_type_id FROM person WHERE email = %s", (email,)
        )
        user_data = cursor.fetchone()

        if user_data:
            email = user_data[0]
            name = user_data[1]
            role_id = user_data[2]
            if role_id == 1:
                role = "admin"
            else:
                role = "teacher"

            user = {"email": email, "name": name, "role": role}
            # Render profile template with user data
            return render_template("profile.html", user=user)
            # return redirect(
            #   url_for("home", from_profile=True)
            # )  # If the user is not logged in, redirect to the login page
    return redirect(url_for("login"))


@app.route("/home")
def home():
    # Check if the redirection is from the profile route
    from_profile = request.args.get("from_profile", False)

    # Render the home page
    return render_template(
        "home.html", user=session.get("user") if from_profile else None
    )


def home1():
    return render_template(
        "home.html", name=session.get("name"), role=session.get("role")
    )


@app.route("/logout")
def logout():
    # Remove user's email from the session
    session.pop("email", None)
    return render_template("login.html")


@app.route("/createaccount")
def createaccount():
    return render_template("add_teacher.html")


# connect to mysql
@app.route("/")
def welcome():
    return render_template("add_teacher.html")


mydb = mysql.connector.Connect(
    host="127.0.0.1", user="developer", password="1234", database="project"
)


@app.route("/teacher/add_teacher", methods=["POST", "GET"])
def add_teacher():

    if request.method == "POST":
        uname = request.form[("username")]
        email = request.form[("email")]
        addresss = request.form[("address")]
        phone = request.form[("phone")]
        schoolname = request.form[("schools")]
        qualify = request.form[("qualification")]
        role = request.form[("role_type")]
        passw = request.form[("password")]

        # p = request.form[("person_id")]

        cur = mydb.cursor()
        # fetch roletype_id
        q = "select id from role_type where name=%s"
        cur.execute(q, (role,))
        role_type_id = cur.fetchone()[0]
        print(role_type_id)

        # insert query values into person
        qu = "INSERT INTO person ( name, email, address, phone, role_type_id, password) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (uname, email, addresss, phone, role_type_id, passw)
        cur.execute(qu, val)
        mydb.commit()
        cur.execute("select *from person")
        r = cur.fetchall()
        print(r)
        # fetch person id
        que = "select id from person where email=%s"

        cur.execute(que, (email,))
        personid = cur.fetchone()[0]
        print(personid)
        # fetch school id
        cur.execute("SELECT id FROM school WHERE name=%s", (schoolname,))
        school_row = cur.fetchone()[0]
        print(school_row)

        # insert values into school_teacher_mapping
        # Insert values into school_teacher_mapping
        quer = "INSERT INTO school_teacher_mapping( school_id, qualification, person_id) VALUES ( %s, %s, %s)"
        da = (school_row, qualify, personid)
        cur.execute(quer, da)

        mydb.commit()
        cur.close()
        mydb.close()
    return "teacher data successfully inserted"


@app.route("/")
def hello():
    return render_template("add_student.html")


mydb = mysql.connector.Connect(
    host="127.0.0.1", user="developer", password="1234", database="project"
)


@app.route("/student/add_student", methods=["GET", "POST", "PUT", "DELETE"])
def add_student():
    if request.method == "GET":
        return studentService.render_add_student()
    elif request.method == "POST":
        return studentService.add_student(request.form)
    return


def convert_to_dict(results):
    # Convert query results to a list of dictionaries for easier access in templates
    keys = [
        "id",
        "name",
        "reason",
        "year_of_dropout",
        "attendance",
        "address",
        "school_id",
        "addhar_number",
        "phone",
        "added_by",
    ]
    return [dict(zip(keys, row)) for row in results]


@app.route("/studentsdata", methods=["GET", "POST"])
def get_student_data():
    if request.method == "GET":
        print("coming here")
        mydb = initialize_db()
        cursor = mydb.cursor()
        email = session.get("email")
        # email = "venugopal.v0308@gmail.com"
        query = "SELECT id, role_type_id FROM person WHERE email = %s"
        cursor.execute(query, (email,))
        user_info = cursor.fetchone()

        if user_info:
            role_id = user_info[1]
            if role_id == 1:
                role = "admin"
                cursor.execute("SELECT * FROM student")
                students_data = cursor.fetchall()
                students = convert_to_dict(students_data)
                cursor.close()
                mydb.close()
                print(students)
                return render_template("studentdata.html", students=students, role=role)
            else:
                role = "teacher"
                teacher_id = user_info[0]
                cursor.execute(
                    "select *from student where added_by in(select id from person where email=%s)",
                    (email,),
                )
                students_data = cursor.fetchall()
                print(students_data, "student data")
                students = convert_to_dict(students_data)
                cursor.close()
                mydb.close()
                return render_template("studentdata.html", students=students, role=role)

    return render_template("studentdata.html", students=[], role="")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_query = request.form.get("search_query")

        mydb = initialize_db()
        cursor = mydb.cursor()

        # Constructing the query to search for matching records
        query = "SELECT * FROM student WHERE name LIKE %s"
        cursor.execute(query, ("%" + search_query + "%",))
        search_results = cursor.fetchall()
        search_results = convert_to_dict(search_results)

        cursor.close()
        mydb.close()

        return render_template("studentdata.html", search_results=search_results)

    return render_template("studentdata.html")


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    mydb = initialize_db()
    cursor = mydb.cursor()

    query = "DELETE FROM student WHERE id = %s"
    cursor.execute(query, (student_id,))
    mydb.commit()

    cursor.close()
    mydb.close()

    return redirect("/studentsdata")


def get_schools():
    mydb = initialize_db()
    cursor = mydb.cursor()
    cursor.execute("SELECT id, name, address FROM school")
    schools = cursor.fetchall()
    cursor.close()
    mydb.close()

    return schools


@app.route("/schools")
def display_schools():
    schools = get_schools()
    return render_template("school_info.html", schools=schools)


if __name__ == "__main__":
    app.secret_key = "super_secret_key"  # Required for session management
    app.run(debug=True)
