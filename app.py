from flask import Flask, render_template, url_for, request, redirect, session, flash, abort
from datetime import timedelta
import sqlite3
import time


app = Flask(__name__)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=60)
db_locale = 'nutrition.db'


def get_db_connection():
    """establishes connection with nutrition.db"""
    conn = sqlite3.connect('db_locale')
    conn.row_factory = sqlite3.Row
    return conn


def get_activity(activity_id):
    """returns activity details by activity id"""
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    activity = c.execute("""SELECT * FROM activity_log WHERE id = ?""",
                         (activity_id,)).fetchone()
    c.close()
    if activity is None:
        abort(404)
    return activity


def get_food(food_id):
    """returns food details by food id"""
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    food = c.execute("""SELECT * FROM food_log WHERE id = ?""",
                         (food_id,)).fetchone()
    c.close()
    if food is None:
        abort(404)
    return food


def get_calories(keyword):
    """returns calories/serving size from microservice calorie_service.py"""
    keyword = str(keyword)
    with open('init_search.txt', 'w') as f:
        f.write('run')
    with open('keyword.txt', 'w') as f:
        f.write(keyword)
    time.sleep(4)
    with open('calories.txt', 'r') as f:
        calories = f.readline()
        portion = f.readline()
    open('calories.txt', 'w').close()
    return calories.rstrip(), portion


def get_curr_goal(goal_id):
    """returns calorie goal from cal_goal db"""
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""SELECT * FROM cal_goal""")
    goal = c.fetchone()
    return goal


@app.route("/")
def home():
    """Home page that renders index.html in user interface"""
    if "user" in session:
        user = session["user"]
        flash(f"You are currently logged in, {user}!")
        return render_template("index.html")
    else:
        flash("Please login to use all features of Health Tracker!")
        return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    """login page, creates a permanent session once a user has logged in
    login is required for app utilization"""
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        return redirect(url_for("home"))
    else:
        if "user" in session:
            return redirect(url_for("home"))
        return render_template("login.html")


@app.route("/logout/")
def logout():
    """logs user out from their session, redirects to login page"""
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))


@app.route("/nutrition/", methods=["POST", "GET"])
def nutrition():
    if "user" in session:
        food_data, total_cals, burn, goal = query_food_details(), total_calories(), cal_burned(), get_goal()
        if request.method == 'POST':
            keyword = request.form['keyword']
            calories = get_calories(keyword)
            data = search_list(calories)
            food_cal, food_serv = data[0], data[1]
            return render_template("nutrition.html", food_data=food_data, total_cals=total_cals, food_cal=food_cal,
                                   food_serv=food_serv, goal=goal, burn=burn)
        return render_template("nutrition.html", food_data=food_data, total_cals=total_cals, goal=goal, burn=burn)
    return redirect(url_for("login"))


def search_list(calories):
    """converts tuple from calorie service to list"""
    data = []
    for i in calories:
        data.append(i)
    return data


#def list_cal_grams(calories):
    #data = []
    #for i in calories:
        #data.append(i)
    #food_cal = data[0]
    #food_serv = data[1]
    #return [food_cal, food_serv]


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


def cal_burned():
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""SELECT SUM(calories) FROM activity_log
    """)
    burned = c.fetchone()
    return burned


def get_goal():
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""SELECT calories FROM cal_goal""")
    goal = c.fetchone()
    return goal


@app.route('/edit_goal/', methods=('GET', 'POST'))
def edit_goal():
    id = 1
    goal = get_curr_goal(id)
    if request.method == 'POST':
        calories = request.form['goal']
        update_goal_db(calories, id)
        return redirect(url_for('nutrition'))
    return render_template('edit_goal.html', goal=goal)


def update_goal_db(calories, id):
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""
                UPDATE cal_goal SET calories= ?"""
              """WHERE id = ?""", (calories, id))
    conn.commit()
    conn.close()
    return


@app.route('/add_food/', methods=('GET', 'POST'))
def add_food():
    if request.method == 'POST':
        name, portion, calories = request.form['name'], request.form['portion'], request.form['calories']
        description = request.form['description']
        add_food_db(name, portion, calories, description)
        return redirect(url_for('nutrition'))
    return render_template('add_food.html')


def add_food_db(name, portion, calories, description):
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""
                INSERT INTO food_log (name, portion, calories, description) VALUES (?, ?, ?, ?)
                """, (name, portion, calories, description))
    conn.commit()
    conn.close()
    return


@app.route('/<int:id>/edit_food/', methods=('GET', 'POST'))
def edit_food(id):
    food = get_food(id)
    if request.method == 'POST':
        name, portion, calories = request.form['name'], request.form['portion'], request.form['calories']
        description = request.form['description']
        update_food_db(name, portion, calories, description, id)
        return redirect(url_for('nutrition'))
    return render_template('edit_food.html', food=food)


def update_food_db(name, portion, calories, description, id):
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""
                UPDATE food_log SET name = ?, portion= ?, calories= ?, description= ?"""
              """WHERE id = ?""", (name, portion, calories, description, id))
    conn.commit()
    conn.close()
    return


@app.route('/<int:id>/delete_food/', methods=('GET', 'POST'))
def delete_food(id):
    get_food(id)
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""DELETE FROM food_log WHERE id = ?""", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('nutrition'))


@app.route("/fitness/", methods=["POST", "GET"])
def fitness():
    if "user" in session:
        user = session["user"]
        activity_data = query_activity_details()
        flash(f"You are currently logged in, {user}! Should you wish to logout hit "
              f"the logout button in the navigation bar. WARNING: You will be logged "
              f"out immediately!")
        return render_template("fitness.html", activity_data=activity_data)
    else:
        flash("Please login to access the Fitness Page! Logging in helps save your data.")
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
        name, length = request.form['name'], request.form['length']
        calories, description = request.form['calories'], request.form['description']
        add_activity_db(name, length, calories, description)
        return redirect(url_for('fitness'))
    return render_template('add_activity.html')


def add_activity_db(name, length, calories, description):
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""
                INSERT INTO activity_log (name, length, calories, description) VALUES (?, ?, ?, ?)
                """, (name, length, calories, description))
    conn.commit()
    conn.close()
    return


@app.route('/<int:id>/edit_activity/', methods=('GET', 'POST'))
def edit_activity(id):
    activity = get_activity(id)
    if request.method == 'POST':
        name, length = request.form['name'], request.form['length']
        calories, description = request.form['calories'], request.form['description']
        update_activity_db(name, length, calories, description, id)
        return redirect(url_for('fitness'))
    return render_template('edit_activity.html', activity=activity)


def update_activity_db(name, length, calories, description, id):
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""
                UPDATE activity_log SET name = ?, length= ?, calories= ?, description= ?"""
              """WHERE id = ?""", (name, length, calories, description, id))
    conn.commit()
    conn.close()
    return


@app.route('/<int:id>/delete_activity/', methods=('GET', 'POST'))
def delete_activity(id):
    get_activity(id)
    conn = sqlite3.connect(db_locale)
    c = conn.cursor()
    c.execute("""DELETE FROM activity_log WHERE id = ?""", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('fitness'))


if __name__ == "__main__":
    app.run(debug=True)
