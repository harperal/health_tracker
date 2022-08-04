from flask import Flask, render_template, url_for, request, redirect, session, flash, abort
from datetime import timedelta
import sqlite3
import time


app = Flask(__name__)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=60)
db_locale = 'nutrition.db'


def get_db_connection():
    conn = sqlite3.connect('db_locale')
    conn.row_factory = sqlite3.Row
    return conn


def get_activity(activity_id):
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    activity = c.execute("""SELECT * FROM activity_log WHERE id = ?""",
                         (activity_id,)).fetchone()
    c.close()
    if activity is None:
        abort(404)
    return activity


def get_food(food_id):
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    food = c.execute("""SELECT * FROM activity_log WHERE id = ?""",
                         (food_id,)).fetchone()
    c.close()
    if food is None:
        abort(404)
    return food


def get_calories(keyword):
    keyword = str(keyword)
    with open('init_search.txt', 'w') as f:
        f.write('run')
    with open('keyword.txt', 'w') as f:
        f.write(keyword)
    time.sleep(6)
    with open('calories.txt', 'r') as f:
        calories = f.readline()
        portion = f.readline()
    open('calories.txt', 'w').close()
    return calories.rstrip(), portion


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
        food_data = query_food_details()
        total_cals = total_calories()
        goal = get_goal()
        if request.method == 'POST':
            keyword = request.form['keyword']
            calories = get_calories(keyword)
            data = []
            for i in calories:
                data.append(i)
            food_cal = data[0]
            food_serv = data[1]
            return render_template("nutrition.html", food_data=food_data, total_cals=total_cals, food_cal=food_cal,
                                   food_serv=food_serv, goal=goal)
        flash(f"You are currently logged in, {user}! Should you wish to logout hit the logout button in the navigation "
              f"bar. WARNING: You will be logged out immediately!")
        return render_template("nutrition.html", food_data=food_data, total_cals=total_cals, goal=goal)
    else:
        flash("Please login to access the Nutrition Page!")
        flash("Logging in allows Health Tracker to save your data and tailor the application to your needs!")
        return redirect(url_for("login"))


def query_food_details():
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""
    SELECT * FROM food_log
    """)
    food_data = c.fetchall()
    return food_data


def total_calories():
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""SELECT SUM(calories) FROM food_log
    """)
    total_cals = c.fetchone()
    return total_cals


def get_goal():
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""SELECT calories FROM cal_goal""")
    goal = c.fetchone()
    return goal


@app.route('/add_food/', methods=('GET', 'POST'))
def add_food():
    if request.method == 'POST':
        name = request.form['name']
        portion = request.form['portion']
        calories = request.form['calories']
        description = request.form['description']
        if not name:
            flash('Food name required')
        elif not portion:
            flash('Food Portion required')
        elif not calories:
            flash('Calories in food required')
        else:
            conn = sqlite3.connect(db_locale)
            c = conn.cursor()
            c.execute("""
                INSERT INTO food_log (name, portion, calories, description) VALUES (?, ?, ?, ?)
                """, (name, portion, calories, description))
            conn.commit()
            conn.close()
            return redirect(url_for('nutrition'))
    return render_template('add_food.html')


@app.route('/<int:id>/edit_food/', methods=('GET', 'POST'))
def edit_food(id):
    food = get_food(id)
    if request.method == 'POST':
        name = request.form['name']
        portion = request.form['portion']
        calories = request.form['calories']
        description = request.form['description']
        if not name:
            flash('Food name required')
        elif not portion:
            flash('Food Portion required')
        elif not calories:
            flash('Calories in food required')
        else:
            conn = sqlite3.connect(db_locale)
            c = conn.cursor()
            c.execute("""
                        UPDATE food_log SET name = ?, portion= ?, calories= ?, description= ?""" 
                      """WHERE id = ?""", (name, portion, calories, description, id))
            conn.commit()
            conn.close()
            return redirect(url_for('nutrition'))
    return render_template('edit_food.html', food=food)


@app.route('/<int:id>/delete_food/', methods=('GET', 'POST'))
def delete_food(id):
    food = get_food(id)
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""DELETE FROM food_log WHERE id = ?""", (id,))
    conn.commit()
    conn.close()
    flash("Successfully Deleted!")
    return redirect(url_for('nutrition'))


@app.route("/fitness/", methods=["POST", "GET"])
def fitness():
    if "user" in session:
        user = session["user"]
        activity_data = query_activity_details()
        flash(f"You are currently logged in, {user}! Should you wish to logout hit the logout button in the navigation "
              f"bar. WARNING: You will be logged out immediately!")
        return render_template("fitness.html", activity_data=activity_data)
    else:
        flash("Please login to access the Fitness Page!")
        flash("Logging in allows Health Tracker to save your data and tailor the application to your needs!")
        return redirect(url_for("login"))


def query_activity_details():
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""
    SELECT * FROM activity_log
    """)
    activity_data = c.fetchall()
    return activity_data


@app.route('/add_activity/', methods=('GET', 'POST'))
def add_activity():
    if request.method == 'POST':
        name = request.form['name']
        length = request.form['length']
        calories = request.form['calories']
        description = request.form['description']
        if not name:
            flash('Activity name required')
        elif not length:
            flash('Activity length required')
        elif not calories:
            flash('Calories burned required')
        else:
            conn = sqlite3.connect(db_locale)
            c = conn.cursor()
            c.execute("""
                INSERT INTO activity_log (name, length, calories, description) VALUES (?, ?, ?, ?)
                """, (name, length, calories, description))
            conn.commit()
            conn.close()
            return redirect(url_for('fitness'))
    return render_template('add_activity.html')


@app.route('/<int:id>/edit_activity/', methods=('GET', 'POST'))
def edit_activity(id):
    activity = get_food(id)
    if request.method == 'POST':
        name = request.form['name']
        length = request.form['length']
        calories = request.form['calories']
        description = request.form['description']
        if not name:
            flash('Activity name required')
        elif not length:
            flash('Activity length required')
        elif not calories:
            flash('Calories burned required')
        else:
            conn = sqlite3.connect(db_locale)
            c = conn.cursor()
            c.execute("""
                        UPDATE activity_log SET name = ?, length= ?, calories= ?, description= ?""" 
                      """WHERE id = ?""", (name, length, calories, description, id))
            conn.commit()
            conn.close()
            return redirect(url_for('fitness'))
    return render_template('edit_activity.html', activity=activity)


@app.route('/<int:id>/delete_activity/', methods=('GET', 'POST'))
def delete_activity(id):
    activity = get_activity(id)
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""DELETE FROM activity_log WHERE id = ?""", (id,))
    conn.commit()
    conn.close()
    flash("Successfully Deleted!")
    return redirect(url_for('fitness'))


if __name__ == "__main__":
    app.run(debug=True)
