import os
import secrets

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

# A brand-new random key is generated every time the app starts.
# This intentionally invalidates every previously issued session
# cookie, so everyone (admin and masters) must log in again after
# any server restart. Set SECRET_KEY in .env instead if you ever
# want sessions to survive a restart.
app.config["SECRET_KEY"] = secrets.token_hex(32)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


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

    master = db.relationship(
        "Master",
        backref="students"
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
# CURRENT ADMIN CHECK
# =========================================================

def is_admin():

    return (
        session.get("logged_in") is True
        and session.get("user_role") == "admin"
    )


# =========================================================
# CURRENT MASTER CHECK
# =========================================================

def is_master():

    return (
        session.get("logged_in") is True
        and session.get("user_role") == "master"
        and session.get("master_id") is not None
    )


# =========================================================
# CURRENT MASTER ID
# =========================================================

def current_master_id():

    if is_master():
        return session.get("master_id")

    return None


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not session.get("logged_in"):

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

        if not session.get("logged_in"):

            flash(
                "Please login first.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        if session.get("user_role") != "admin":

            flash(
                "Admin access required.",
                "error"
            )

            return redirect(
                url_for("master_dashboard")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# =========================================================
# MASTER REQUIRED
# =========================================================

def master_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not session.get("logged_in"):

            flash(
                "Please login first.",
                "error"
            )

            return redirect(
                url_for("master_login")
            )

        if session.get("user_role") != "master":

            flash(
                "Master access required.",
                "error"
            )

            return redirect(
                url_for("dashboard")
            )

        if not session.get("master_id"):

            session.clear()

            flash(
                "Master session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("master_login")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        if is_admin():

            return redirect(
                url_for("dashboard")
            )

        if is_master():

            return redirect(
                url_for("master_dashboard")
            )

        return render_template(
            "admin_login.html"
        )


    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )


    if not username or not password:

        return render_template(
            "admin_login.html",
            error="Please enter username and password."
        )


    admin = Admin.query.filter_by(
        username=username
    ).first()


    if admin and check_password_hash(
        admin.password_hash,
        password
    ):

        session.clear()

        session["logged_in"] = True
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


    return render_template(
        "admin_login.html",
        error="Invalid admin username or password."
    )


# =========================================================
# SEPARATE MASTER LOGIN
# =========================================================

@app.route(
    "/master-login",
    methods=["GET", "POST"]
)
def master_login():

    if request.method == "GET":

        if is_master():

            return redirect(
                url_for("master_dashboard")
            )

        if is_admin():

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "master_login.html"
        )


    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )


    if not username or not password:

        return render_template(
            "master_login.html",
            error="Please enter username and password."
        )


    master = Master.query.filter_by(
        username=username
    ).first()


    if master and check_password_hash(
        master.password_hash,
        password
    ):

        session.clear()

        session["logged_in"] = True
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
            url_for("master_dashboard")
        )


    return render_template(
        "master_login.html",
        error="Invalid master username or password."
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
# ADMIN DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    if is_master():

        return redirect(
            url_for("master_dashboard")
        )


    total_students = Student.query.count()


    today = date.today().strftime(
        "%Y-%m-%d"
    )


    present_today = Attendance.query.filter_by(
        attendance_date=today,
        status="Present"
    ).count()


    fees_collected = (
        db.session.query(
            db.func.sum(Fee.amount)
        )
        .filter(
            Fee.status == "Paid"
        )
        .scalar()
        or 0
    )


    achievements_count = Achievement.query.count()


    return render_template(
        "dashboard.html",
        total_students=total_students,
        present_today=present_today,
        fees_collected=fees_collected,
        achievements_count=achievements_count
    )


# =========================================================
# MASTER DASHBOARD
# =========================================================

@app.route("/master-dashboard")
@master_required
def master_dashboard():

    master_id = current_master_id()


    master = db.get_or_404(
        Master,
        master_id
    )


    students = Student.query.filter_by(
        master_id=master_id
    ).order_by(
        Student.name
    ).all()


    student_ids = [
        student.id
        for student in students
    ]


    total_students = len(
        student_ids
    )


    today = date.today().strftime(
        "%Y-%m-%d"
    )


    if student_ids:

        present_today = Attendance.query.filter(
            Attendance.attendance_date == today,
            Attendance.status == "Present",
            Attendance.student_id.in_(student_ids)
        ).count()


        fees_collected = (
            db.session.query(
                db.func.sum(Fee.amount)
            )
            .filter(
                Fee.status == "Paid",
                Fee.student_id.in_(student_ids)
            )
            .scalar()
            or 0
        )


        achievements_count = Achievement.query.filter(
            Achievement.student_id.in_(student_ids)
        ).count()

    else:

        present_today = 0
        fees_collected = 0
        achievements_count = 0


    return render_template(
        "master_dashboard.html",
        master=master,
        username=master.username,
        students=students,
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

    master_id = current_master_id()


    if master_id:

        students = Student.query.filter_by(
            master_id=master_id
        ).order_by(
            Student.id.desc()
        ).all()

        # Master must never receive the complete master list.
        masters = []

    else:

        students = Student.query.order_by(
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

    master_id_form = request.form.get(
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


    # =====================================================
    # MASTER
    # Master can ONLY add student to themselves.
    # =====================================================

    if is_master():

        master_id = current_master_id()

        master = db.get_or_404(
            Master,
            master_id
        )

        # Automatically use Master's location/batch
        # when the form does not provide them.

        if not location:
            location = master.location or ""

        if not batch:
            batch = master.batch or ""

    else:

        # ADMIN

        if master_id_form:

            try:

                master_id = int(
                    master_id_form
                )

            except ValueError:

                master_id = None

        else:

            master_id = None


        if master_id:

            selected_master = db.session.get(
                Master,
                master_id
            )

            if not selected_master:

                flash(
                    "Selected master does not exist.",
                    "error"
                )

                return redirect(
                    url_for("students_page")
                )


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


    # Master can delete ONLY their own student.

    if is_master():

        if student.master_id != current_master_id():

            flash(
                "You can only delete your own students.",
                "error"
            )

            return redirect(
                url_for("students_page")
            )


    # Delete related records first.

    Attendance.query.filter_by(
        student_id=student.id
    ).delete(
        synchronize_session=False
    )


    Fee.query.filter_by(
        student_id=student.id
    ).delete(
        synchronize_session=False
    )


    Achievement.query.filter_by(
        student_id=student.id
    ).delete(
        synchronize_session=False
    )


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
        date.today().strftime("%Y-%m-%d")
    )


    query = Student.query


    if is_master():

        query = query.filter_by(
            master_id=current_master_id()
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


    query = Student.query


    if is_master():

        query = query.filter_by(
            master_id=current_master_id()
        )


    students = query.all()


    for student in students:

        status = request.form.get(
            f"status_{student.id}",
            "Absent"
        )


        if status not in [
            "Present",
            "Absent"
        ]:

            status = "Absent"


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


    if is_master():

        student_query = student_query.filter_by(
            master_id=current_master_id()
        )


    students = student_query.order_by(
        Student.name
    ).all()


    student_ids = [
        student.id
        for student in students
    ]


    fees_query = Fee.query


    if is_master():

        if student_ids:

            fees_query = fees_query.filter(
                Fee.student_id.in_(student_ids)
            )

        else:

            fees_query = fees_query.filter(
                db.literal(False)
            )


    fees = fees_query.order_by(
        Fee.id.desc()
    ).all()


    upi_id = os.environ.get(
        "UPI_ID",
        "yourupi@bank"
    )

    upi_name = os.environ.get(
        "UPI_PAYEE_NAME",
        "Silambam Academy"
    )


    return render_template(
        "fees.html",
        students=students,
        fees=fees,
        upi_id=upi_id,
        upi_name=upi_name
    )


# =========================================================
# SAVE FEE
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

    amount_value = request.form.get(
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


    # =====================================================
    # MASTER OWNERSHIP CHECK
    # =====================================================

    if is_master():

        if student.master_id != current_master_id():

            flash(
                "You can only add fees for your own students.",
                "error"
            )

            return redirect(
                url_for("fees_page")
            )


    try:

        amount = float(
            amount_value
        )

    except (
        ValueError,
        TypeError
    ):

        flash(
            "Invalid fee amount.",
            "error"
        )

        return redirect(
            url_for("fees_page")
        )


    if amount < 0:

        flash(
            "Fee amount cannot be negative.",
            "error"
        )

        return redirect(
            url_for("fees_page")
        )


    fee = Fee(
        student_id=student.id,
        month=month,
        amount=amount,
        payment_date=payment_date or date.today().strftime("%Y-%m-%d"),
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


    if is_master():

        student_query = student_query.filter_by(
            master_id=current_master_id()
        )


    students = student_query.order_by(
        Student.name
    ).all()


    student_ids = [
        student.id
        for student in students
    ]


    achievements_query = Achievement.query


    if is_master():

        if student_ids:

            achievements_query = achievements_query.filter(
                Achievement.student_id.in_(student_ids)
            )

        else:

            achievements_query = achievements_query.filter(
                db.literal(False)
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
# SAVE ACHIEVEMENT
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


    if not student:

        flash(
            "Please select a valid student.",
            "error"
        )

        return redirect(
            url_for("achievements_page")
        )


    if not event or not achievement_date or not position:

        flash(
            "Please fill all required achievement details.",
            "error"
        )

        return redirect(
            url_for("achievements_page")
        )


    # =====================================================
    # MASTER OWNERSHIP CHECK
    # =====================================================

    if is_master():

        if student.master_id != current_master_id():

            flash(
                "You can only add achievements for your own students.",
                "error"
            )

            return redirect(
                url_for("achievements_page")
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
        url_for("achievements_page")
    )


# =========================================================
# ADMIN ONLY - MASTERS PAGE
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
# ADMIN ONLY - ADD MASTER
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
            url_for("masters_page")
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
            url_for("masters_page")
        )


    try:

        latitude_value = (
            float(latitude)
            if latitude
            else None
        )

        longitude_value = (
            float(longitude)
            if longitude
            else None
        )

    except ValueError:

        flash(
            "Invalid map coordinates.",
            "error"
        )

        return redirect(
            url_for("masters_page")
        )


    master = Master(
        name=name,
        username=username,
        password_hash=generate_password_hash(
            password
        ),
        location=location,
        latitude=latitude_value,
        longitude=longitude_value,
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
        url_for("masters_page")
    )


# =========================================================
# ADMIN ONLY - DELETE MASTER
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


    # -----------------------------------------------------
    # Do not delete students.
    # Their master_id becomes NULL.
    # -----------------------------------------------------

    students = Student.query.filter_by(
        master_id=master.id
    ).all()


    for student in students:

        student.master_id = None


    db.session.delete(
        master
    )

    db.session.commit()


    flash(
        "Master deleted successfully. Their students were kept safely.",
        "success"
    )


    return redirect(
        url_for("masters_page")
    )


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    with app.app_context():

        db.create_all()


        # =================================================
        # CREATE DEFAULT ADMIN
        # =================================================

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

        else:

            # If ADMIN_PASSWORD changes in .env,
            # update the existing admin password.

            if not check_password_hash(
                admin.password_hash,
                admin_password
            ):

                admin.password_hash = (
                    generate_password_hash(
                        admin_password
                    )
                )

                db.session.commit()


        # =================================================
        # ENFORCE A SINGLE ADMIN ACCOUNT
        #
        # If ADMIN_USERNAME in .env was changed, any older
        # admin account(s) with a different username are
        # removed automatically, so only the one matching
        # .env can ever log in.
        # =================================================

        Admin.query.filter(
            Admin.username != admin_username
        ).delete(
            synchronize_session=False
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
