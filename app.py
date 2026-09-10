from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"  # TODO: move to an env var before deploying

# ---------------------------------------------------------------------------
# TEMPORARY hardcoded credentials.
# Replace this with a real database (e.g. SQLAlchemy + hashed passwords)
# once you're ready — this is just so Admin vs Master login actually works.
# ---------------------------------------------------------------------------
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}
MASTER_CREDENTIALS = {"username": "master", "password": "master123"}


def login_required(role):
    """Decorator: only let a request through if session['role'] matches."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get("role") != role:
                flash("Please log in to continue.")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    role = request.form.get("role")
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if role == "admin" and username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
        session["role"] = "admin"
        session["username"] = username
        return redirect(url_for("admin_dashboard"))

    if role == "master" and username == MASTER_CREDENTIALS["username"] and password == MASTER_CREDENTIALS["password"]:
        session["role"] = "master"
        session["username"] = username
        return redirect(url_for("master_dashboard"))

    flash("Invalid username, password, or role.")
    return redirect(url_for("home"))


@app.route("/dashboard/admin")
@login_required("admin")
def admin_dashboard():
    return render_template("admin_dashboard.html", username=session.get("username"))


@app.route("/dashboard/master")
@login_required("master")
def master_dashboard():
    return render_template("master_dashboard.html", username=session.get("username"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
