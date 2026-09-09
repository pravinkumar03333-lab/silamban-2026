import os

from dotenv import load_dotenv
from datetime import date
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "silambam-secret-key-2026"
)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

database_url = os.environ.get("DATABASE_URL")

if database_url:

    if database_url.startswith("postgres://"):

        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///silambam.db"
    )


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


# =========================================================
# ADMIN MODEL
# =========================================================

class Admin(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )


# =========================================================
# MASTER MODEL
# =========================================================

class Master(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    location = db.Column(
        db.String(200),
        nullable=True
    )

    latitude = db.Column(
        db.Float,
        nullable=True
    )

    longitude = db.Column(
        db.Float,
        nullable=True
    )

    batch = db.Column(
        db.String(100),
        nullable=True
    )


# =========================================================
# STUDENT MODEL
# =========================================================

class Student(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    age = db.Column(
        db.Integer,
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        nullable=False
    )

    belt = db.Column(
        db.String(50),
        nullable=False
    )

    join_date = db.Column(
        db.String(20),
        nullable=False
    )

    master_id = db.Column(
        db.Integer,
        db.ForeignKey("master.id"),
        nullable=True
    )

    location = db.Column(
        db.String(200),
        nullable=True
    )

    batch = db.Column(
        db.String(100),
        nullable=True
    )


# =========================================================
# ATTENDANCE MODEL
# =========================================================

class Attendance(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    attendance_date = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False
    )

    student = db.relationship(
        "Student"
    )


# =========================================================
# FEE MODEL
# =========================================================

class Fee(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    month = db.Column(
        db.String(20),
        nullable=True
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    payment_date = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False
    )

    student = db.relationship(
        "Student"
    )


# =========================================================
# ACHIEVEMENT MODEL
# =========================================================

class Achievement(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    event = db.Column(
        db.String(200),
        nullable=False
    )

    location = db.Column(
        db.String(200),
        nullable=True
    )

    position = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    achievement_date = db.Column(
        db.String(20),
        nullable=False
    )

    student = db.relationship(
        "Student"
    )


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(function):

    @wraps(function)

    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# =========================================================
# ADMIN REQUIRED
# =========================================================

def admin_required(function):

    @wraps(function)

    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            return redirect(
                url_for("login")
            )

        if session.get("user_role") != "admin":

            flash(
                "Admin access required.",
                "error"
            )

            return redirect(
                url_for("dashboard")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# =========================================================
# CURRENT MASTER HELPER
#
# Returns the logged-in master's id if the current session
# belongs to a master, otherwise None (admin sees everything).
# =========================================================

def current_master_id():

    if session.get("user_role") == "master":

        return session.get("master_id")

    return None


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# LOGIN
#
# IMPORTANT:
# GET  -> Opens login page
# POST -> Processes login
#
# This fixes "Method Not Allowed"
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # Already logged in
    if request.method == "GET":

        if "user_id" in session:

            return redirect(
                url_for("dashboard")
            )


    # Process Login
    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            "admin"
        )


        # =================================================
        # ADMIN LOGIN
        # =================================================

        if role == "admin":

            admin = Admin.query.filter_by(
                username=username
            ).first()


            if admin and check_password_hash(
                admin.password_hash,
                password
            ):

                session.clear()

                session["user_id"] = admin.id

                session["user_role"] = "admin"

                session["username"] = admin.username


                flash(
                    "Admin login successful!",
                    "success"
                )


                return redirect(
                    url_for("dashboard")
                )


        # =================================================
        # MASTER LOGIN
        # =================================================

        elif role == "master":

            master = Master.query.filter_by(
                username=username
            ).first()


            if master and check_password_hash(
                master.password_hash,
                password
            ):

                session.clear()

                session["user_id"] = master.id

                session["user_role"] = "master"

                session["username"] = master.username

                session["master_id"] = master.id

                session["master_name"] = master.name


                flash(
                    "Master login successful!",
                    "success"
                )


                return redirect(
                    url_for("dashboard")
                )


        flash(
            "Invalid username, password or login type.",
            "error"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()


    flash(
        "You have logged out successfully.",
        "success"
    )


    return redirect(
        url_for("home")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    master_id = current_master_id()

    student_query = Student.query

    if master_id:

        student_query = student_query.filter_by(
            master_id=master_id
        )

    total_students = student_query.count()

    my_student_ids = [
        s.id for s in student_query.all()
    ]


    today = date.today().strftime(
        "%Y-%m-%d"
    )


    attendance_query = Attendance.query.filter_by(
        attendance_date=today,
        status="Present"
    )

    if master_id:

        attendance_query = attendance_query.filter(
            Attendance.student_id.in_(my_student_ids)
        )

    present_today = attendance_query.count()


    fees_query = db.session.query(
        db.func.sum(
            Fee.amount
        )
    ).filter(
        Fee.status == "Paid"
    )

    if master_id:

        fees_query = fees_query.filter(
            Fee.student_id.in_(my_student_ids)
        )

    fees_collected = fees_query.scalar() or 0


    achievements_query = Achievement.query

    if master_id:

        achievements_query = achievements_query.filter(
            Achievement.student_id.in_(my_student_ids)
        )

    achievements_count = achievements_query.count()


    return render_template(

        "dashboard.html",

        total_students=total_students,

        present_today=present_today,

        fees_collected=fees_collected,

        achievements_count=achievements_count

    )


# =========================================================
# STUDENTS
# =========================================================

@app.route("/students")
@login_required
def students_page():

    query = Student.query

    master_id = current_master_id()

    if master_id:

        query = query.filter_by(
            master_id=master_id
        )

    students = query.order_by(
        Student.id.desc()
    ).all()


    masters = Master.query.order_by(
        Master.name
    ).all()


    return render_template(

        "students.html",

        students=students,

        masters=masters

    )


# =========================================================
# ADD STUDENT
# =========================================================

@app.route(
    "/add_student",
    methods=["POST"]
)
@login_required
def add_student():

    name = request.form.get(
        "name",
        ""
    ).strip()


    age = request.form.get(
        "age",
        ""
    ).strip()


    phone = request.form.get(
        "phone",
        ""
    ).strip()


    belt = request.form.get(
        "belt",
        ""
    ).strip()


    join_date = request.form.get(
        "join_date",
        ""
    ).strip()


    master_id = request.form.get(
        "master_id"
    )


    location = request.form.get(
        "location",
        ""
    ).strip()


    batch = request.form.get(
        "batch",
        ""
    ).strip()


    if not all([
        name,
        age,
        phone,
        belt,
        join_date
    ]):

        flash(
            "Please fill all required student details.",
            "error"
        )

        return redirect(
            url_for("students_page")
        )


    try:

        age = int(age)

    except ValueError:

        flash(
            "Age must be a number.",
            "error"
        )

        return redirect(
            url_for("students_page")
        )


    if master_id:

        master_id = int(
            master_id
        )

    else:

        master_id = None


    # A logged-in master can only ever add students to
    # themselves, regardless of what the form sent.
    if current_master_id():

        master_id = current_master_id()


    student = Student(

        name=name,

        age=age,

        phone=phone,

        belt=belt,

        join_date=join_date,

        master_id=master_id,

        location=location,

        batch=batch

    )


    db.session.add(
        student
    )

    db.session.commit()


    flash(
        "Student added successfully.",
        "success"
    )


    return redirect(
        url_for("students_page")
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@app.route(
    "/delete_student/<int:student_id>",
    methods=["POST"]
)
@login_required
def delete_student(student_id):

    student = db.get_or_404(
        Student,
        student_id
    )


    master_id = current_master_id()

    if master_id and student.master_id != master_id:

        flash(
            "You can only delete your own students.",
            "error"
        )

        return redirect(
            url_for("students_page")
        )


    Attendance.query.filter_by(
        student_id=student.id
    ).delete()


    Fee.query.filter_by(
        student_id=student.id
    ).delete()


    Achievement.query.filter_by(
        student_id=student.id
    ).delete()


    db.session.delete(
        student
    )


    db.session.commit()


    flash(
        "Student deleted successfully.",
        "success"
    )


    return redirect(
        url_for("students_page")
    )


# =========================================================
# ATTENDANCE PAGE
# =========================================================

@app.route("/attendance")
@login_required
def attendance_page():

    selected_date = request.args.get(

        "date",

        date.today().strftime(
            "%Y-%m-%d"
        )

    )


    query = Student.query

    master_id = current_master_id()

    if master_id:

        query = query.filter_by(
            master_id=master_id
        )

    students = query.order_by(
        Student.name
    ).all()


    return render_template(

        "attendance.html",

        students=students,

        selected_date=selected_date

    )


# =========================================================
# SAVE ATTENDANCE
# =========================================================

@app.route(
    "/save_attendance",
    methods=["POST"]
)
@login_required
def save_attendance():

    attendance_date = request.form.get(
        "attendance_date"
    )


    if not attendance_date:

        flash(
            "Please select attendance date.",
            "error"
        )

        return redirect(
            url_for("attendance_page")
        )


    students = Student.query

    master_id = current_master_id()

    if master_id:

        students = students.filter_by(
            master_id=master_id
        )

    students = students.all()


    for student in students:

        status = request.form.get(

            f"status_{student.id}",

            "Absent"

        )


        existing = Attendance.query.filter_by(

            student_id=student.id,

            attendance_date=attendance_date

        ).first()


        if existing:

            existing.status = status

        else:

            record = Attendance(

                student_id=student.id,

                attendance_date=attendance_date,

                status=status

            )


            db.session.add(
                record
            )


    db.session.commit()


    flash(
        "Attendance saved successfully.",
        "success"
    )


    return redirect(

        url_for(

            "attendance_page",

            date=attendance_date

        )

    )


# =========================================================
# FEES
# =========================================================

@app.route("/fees")
@login_required
def fees_page():

    student_query = Student.query

    master_id = current_master_id()

    my_student_ids = None

    if master_id:

        student_query = student_query.filter_by(
            master_id=master_id
        )

        my_student_ids = [
            s.id for s in student_query.all()
        ]

    students = student_query.order_by(
        Student.name
    ).all()


    fees_query = Fee.query

    if my_student_ids is not None:

        fees_query = fees_query.filter(
            Fee.student_id.in_(my_student_ids)
        )

    fees = fees_query.order_by(
        Fee.id.desc()
    ).all()


    return render_template(

        "fees.html",

        students=students,

        fees=fees

    )


# =========================================================
# ADD FEE
# =========================================================

@app.route(
    "/save_fee",
    methods=["POST"]
)
@login_required
def save_fee():

    student_name = request.form.get(
        "student",
        ""
    ).strip()


    month = request.form.get(
        "month",
        ""
    ).strip()


    amount = request.form.get(
        "amount"
    )


    status = request.form.get(
        "status",
        "Pending"
    )


    payment_date = request.form.get(
        "date"
    )


    student = Student.query.filter_by(
        name=student_name
    ).first()


    if not student:

        flash(
            "Please select a valid student.",
            "error"
        )

        return redirect(
            url_for("fees_page")
        )


    master_id = current_master_id()

    if master_id and student.master_id != master_id:

        flash(
            "You can only add fees for your own students.",
            "error"
        )

        return redirect(
            url_for("fees_page")
        )


    try:

        amount = float(
            amount
        )

    except (
        ValueError,
        TypeError
    ):

        flash(
            "Invalid fee information.",
            "error"
        )

        return redirect(
            url_for("fees_page")
        )


    fee = Fee(

        student_id=student.id,

        month=month,

        amount=amount,

        payment_date=payment_date,

        status=status

    )


    db.session.add(
        fee
    )

    db.session.commit()


    flash(
        "Fee added successfully.",
        "success"
    )


    return redirect(
        url_for("fees_page")
    )


# =========================================================
# ACHIEVEMENTS
# =========================================================

@app.route("/achievements")
@login_required
def achievements_page():

    student_query = Student.query

    master_id = current_master_id()

    my_student_ids = None

    if master_id:

        student_query = student_query.filter_by(
            master_id=master_id
        )

        my_student_ids = [
            s.id for s in student_query.all()
        ]

    students = student_query.order_by(
        Student.name
    ).all()


    achievements_query = Achievement.query

    if my_student_ids is not None:

        achievements_query = achievements_query.filter(
            Achievement.student_id.in_(my_student_ids)
        )

    achievements = achievements_query.order_by(
        Achievement.id.desc()
    ).all()


    return render_template(

        "achievements.html",

        students=students,

        achievements=achievements

    )


# =========================================================
# ADD ACHIEVEMENT
# =========================================================

@app.route(
    "/save_achievement",
    methods=["POST"]
)
@login_required
def save_achievement():

    student_name = request.form.get(
        "student",
        ""
    ).strip()


    event = request.form.get(
        "event",
        ""
    ).strip()


    location = request.form.get(
        "location",
        ""
    ).strip()


    achievement_date = request.form.get(
        "date"
    )


    position = request.form.get(
        "position",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    student = Student.query.filter_by(
        name=student_name
    ).first()


    if not student or not event or not achievement_date or not position:

        flash(
            "Please fill all required achievement details.",
            "error"
        )

        return redirect(
            url_for(
                "achievements_page"
            )
        )


    master_id = current_master_id()

    if master_id and student.master_id != master_id:

        flash(
            "You can only add achievements for your own students.",
            "error"
        )

        return redirect(
            url_for(
                "achievements_page"
            )
        )


    achievement = Achievement(

        student_id=student.id,

        event=event,

        location=location,

        position=position,

        description=description,

        achievement_date=achievement_date

    )


    db.session.add(
        achievement
    )

    db.session.commit()


    flash(
        "Achievement added successfully.",
        "success"
    )


    return redirect(
        url_for(
            "achievements_page"
        )
    )


# =========================================================
# MASTERS PAGE
# =========================================================

@app.route("/masters")
@admin_required
def masters_page():

    masters = Master.query.order_by(
        Master.name
    ).all()


    return render_template(

        "masters.html",

        masters=masters

    )


# =========================================================
# ADD MASTER
# =========================================================

@app.route(
    "/add_master",
    methods=["POST"]
)
@admin_required
def add_master():

    name = request.form.get(
        "name",
        ""
    ).strip()


    username = request.form.get(
        "username",
        ""
    ).strip()


    password = request.form.get(
        "password",
        ""
    )


    location = request.form.get(
        "location",
        ""
    ).strip()


    latitude = request.form.get(
        "latitude",
        ""
    ).strip()


    longitude = request.form.get(
        "longitude",
        ""
    ).strip()


    latitude = float(latitude) if latitude else None

    longitude = float(longitude) if longitude else None


    batch = request.form.get(
        "batch",
        ""
    ).strip()


    if not name or not username or not password:

        flash(
            "Name, username and password are required.",
            "error"
        )

        return redirect(
            url_for(
                "masters_page"
            )
        )


    existing = Master.query.filter_by(
        username=username
    ).first()


    if existing:

        flash(
            "This master username already exists.",
            "error"
        )

        return redirect(
            url_for(
                "masters_page"
            )
        )


    master = Master(

        name=name,

        username=username,

        password_hash=generate_password_hash(
            password
        ),

        location=location,

        latitude=latitude,

        longitude=longitude,

        batch=batch

    )


    db.session.add(
        master
    )

    db.session.commit()


    flash(
        "Master added successfully.",
        "success"
    )


    return redirect(
        url_for(
            "masters_page"
        )
    )


# =========================================================
# DELETE MASTER
# =========================================================

@app.route(
    "/delete_master/<int:master_id>",
    methods=["POST"]
)
@admin_required
def delete_master(master_id):

    master = db.get_or_404(
        Master,
        master_id
    )


    db.session.delete(
        master
    )


    db.session.commit()


    flash(
        "Master deleted successfully.",
        "success"
    )


    return redirect(
        url_for(
            "masters_page"
        )
    )


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    with app.app_context():

        db.create_all()


        # ---------------------------------------------
        # CREATE DEFAULT ADMIN
        # ---------------------------------------------

        admin_username = os.environ.get(
            "ADMIN_USERNAME",
            "admin"
        )


        admin_password = os.environ.get(
            "ADMIN_PASSWORD",
            "admin123"
        )


        admin = Admin.query.filter_by(
            username=admin_username
        ).first()


        if not admin:

            admin = Admin(

                username=admin_username,

                password_hash=generate_password_hash(
                    admin_password
                )

            )


            db.session.add(
                admin
            )


            db.session.commit()


# =========================================================
# INITIALIZE DATABASE
# =========================================================

initialize_database()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )