from flask import Flask, render_template,request,redirect,session
import sqlite3

app = Flask(__name__)
app.secret_key = "expense_tracker_secret"

def init_db():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    
    cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
    )
    """)
    

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT
    )
    """)
    

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():

    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM expenses")
    expenses = cur.fetchall()

    conn.close()

    return render_template("index.html",expenses=expenses)

from flask import Flask, render_template, request, redirect

@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():

    if request.method == "POST":

        date = request.form["date"]
        category = request.form["category"]
        amount = request.form["amount"]
        description = request.form["description"]

        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()

        cur.execute("""
                    INSERT INTO expenses(date, category, amount, description)
                    VALUES (?, ?, ?, ?)
                    """, (date, category, amount, description))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_expense.html")

@app.route("/delete/<int:id>")
def delete_expense(id):

    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM expenses WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_expense(id):

    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    if request.method == "POST":

        date = request.form["date"]
        category = request.form["category"]
        amount = request.form["amount"]
        description = request.form["description"]

        cur.execute("""
        UPDATE expenses
        SET date=?,
            category=?,
            amount=?,
            description=?
        WHERE id=?
        """, (date, category, amount, description, id))

        conn.commit()
        conn.close()

        return redirect("/")

    cur.execute(
        "SELECT * FROM expenses WHERE id=?",
        (id,)
    )

    expense = cur.fetchone()

    conn.close()

    return render_template(
        "edit_expense.html",
        expense=expense
    )

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    cur.execute("SELECT SUM(amount) FROM expenses")
    total = cur.fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    return render_template(
        "dashboard.html",
        total=total
    )

@app.route("/search", methods=["GET", "POST"])
def search():

    expenses = []

    if request.method == "POST":

        keyword = request.form["keyword"]

        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM expenses WHERE category LIKE ?",
            ('%' + keyword + '%',)
        )

        expenses = cur.fetchall()
        conn.close()

    return render_template(
        "search.html",
        expenses=expenses
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/")

        return "Invalid Username or Password"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)