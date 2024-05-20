from flask import Flask, render_template, redirect, session, request, jsonify
import models
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import json
from datetime import datetime

from helpers import login_required, apology

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

con = sqlite3.connect("attendance.db", check_same_thread=False)
cursor = con.cursor()
USER = {'username': ''}

# Previous code from app.py
def create_app():
    app = Flask(__name__)
    models.init_db()
    return app

# New code for rendering HTML templates
@app.route('/', methods= ['GET', 'POST'])
@login_required
def index():
    if request.method == "POST":
        attendance_data = request.data
        decoded_data = attendance_data.decode('utf-8')
        attendanceJson = ''
        if decoded_data:
            attendanceJson = request.get_json()
        try:
            cursor.executemany('INSERT INTO attendance (student_id, date, user_id) VALUES (?, ?, ?)', [(data['id'], data['newDate'], int(session["user_id"])) for data in attendanceJson])
            con.commit()
            return redirect("/attendance")
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error": "Failed to fetch data"})
    else:
        cursor.execute("SELECT p.student_id, s.firstname, s.lastname, s.email, SUM(p.class_quantity) - (SELECT COUNT(*) FROM attendance a WHERE a.student_id = p.student_id) AS remaining_class_quantity FROM packages p JOIN students s ON p.student_id = s.id AND s.user_id = ? WHERE p.user_id = ? GROUP BY p.student_id, s.firstname, s.lastname, s.email HAVING SUM(p.class_quantity) - (SELECT COUNT(*) FROM attendance a WHERE a.student_id = p.student_id) > 0 ORDER BY s.firstname ASC", (int(session["user_id"]), int(session["user_id"])))
        packages = cursor.fetchall()
        return render_template("index.html", user=USER['username'], active_link="home", packages = packages)

@app.route('/attendance')
@login_required
def attendance():
    cursor.execute("SELECT a.id, s.firstname, s.lastname, s.email, a.date FROM attendance a JOIN students s ON a.student_id = s.id AND s.user_id = ? WHERE a.user_id = ? ORDER BY a.date DESC", (int(session["user_id"]), int(session["user_id"])))
    attendees = cursor.fetchall()
    return render_template("attendance.html", attendees = attendees)
                    

@app.route('/register_students', methods= ['GET', 'POST'])
@login_required
def register_students():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("first"):
            return apology("must provide first name", 403)
        elif not request.form.get("last"):
            return apology("must provide last name", 403)
        # insert user in table students
        if request.form.get("email") != "":
            cursor.execute("INSERT INTO students (firstname, lastname, email, user_id) VALUES (?, ?, ?, ?)", (request.form.get("first"), request.form.get("last"), request.form.get("email"), int(session["user_id"])) )
            con.commit()
            return redirect('/')
        else:
            cursor.execute("INSERT INTO students (firstname, lastname, user_id) VALUES (?, ?, ?)", (request.form.get("first"), request.form.get("last"), int(session["user_id"])) )
            con.commit()
            return redirect('/')
    else:   
        return render_template("register_students.html",active_link="register_students")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cursor.fetchall()
        num_rows = len(rows)

        # Ensure username exists and password is correct
        if num_rows != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        USER['username'] = rows[0][1]

        # Redirect user to home page
        return redirect('/')


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", active_link="login")
@app.route("/packages", methods=["GET", "POST"])
def packages():
    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    print(dt_string)
    if request.method == "POST":
        cursor.execute("INSERT INTO packages (student_id, class_quantity, purchase_date, user_id) VALUES (?, ?, ?, ?)", (request.form.get("id"), request.form.get("quantity"), dt_string, int(session["user_id"])))
        con.commit()
        print("success")
        return redirect("/packages")
    else:
        cursor.execute("SELECT * FROM students WHERE user_id = ?", (int(session["user_id"]),))
        students = cursor.fetchall()
        return render_template("packages.html", students=students, active_link="packages")
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    usernames = cursor.execute("SELECT username FROM users")
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    users = [ user[0] for user in usernames ]
    if request.method == "POST":
        if not username:
            print("No user name")
            return apology("Must provide a valid username", 400)
        elif username in users:
            return apology("This username is in use", 400)
        elif not password:
            return apology("Must enter a password", 400)
        elif password != confirmation:
            return apology("Password and confirmation must match", 400)
        else:
            hash = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash) )
            con.commit()
            return render_template("login.html")
    else:
        return render_template("register.html", active_link="register")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)