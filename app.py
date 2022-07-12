from flask import Flask, render_template, url_for, request, redirect, session, flash
from datetime import timedelta


app = Flask(__name__)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=60)


@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        flash(f"You are currently logged in, {user}!")
        return render_template("index.html")
    else:
        flash("Please login to use all features of Health Tracker!")
        return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        flash(f"You have successfully logged in, {user}! Should you wish to logout hit the logout button in the"
              f"navigation bar. WARNING: You will be logged out immediately!", "info")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("You are already logged in!")
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/user/", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            flash("Name and email was saved!")
            return redirect(url_for("home"))
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)
    else:
        flash("You are not logged in")
        return redirect(url_for("login.html"))


@app.route("/logout/")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))


@app.route("/nutrition/", methods=["POST", "GET"])
def nutrition():
    if "user" in session:
        user = session["user"]
        flash(f"You are currently logged in, {user}! Should you wish to logout hit the logout button in thenavigation "
              f"bar. WARNING: You will be logged out immediately!")
        return render_template("nutrition.html")
    else:
        flash("Please login to access the Nutrition Page!")
        flash("Logging in allows Health Tracker to save your data and tailor the application to your needs!")
        return redirect(url_for("login"))


@app.route("/fitness/", methods=["POST", "GET"])
def fitness():
    if "user" in session:
        user = session["user"]
        flash(f"You are currently logged in, {user}! Should you wish to logout hit the logout button in thenavigation "
              f"bar. WARNING: You will be logged out immediately!")
        return render_template("fitness.html")
    else:
        flash("Please login to access the Fitness Page!")
        flash("Logging in allows Health Tracker to save your data and tailor the application to your needs!")
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
