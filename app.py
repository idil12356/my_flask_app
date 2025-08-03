from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sir_qarsoon'
DB_NAME = 'quiz.db'

# 🚀 DB INIT
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Questions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    ''')

    # Results table
    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            user_id INTEGER UNIQUE,
            score INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Insert 10 Somalia Questions (only if table is empty)
    c.execute("SELECT COUNT(*) FROM questions")
    if c.fetchone()[0] == 0:
        questions = [
            ("Waa maxay caasimadda Soomaaliya?", "Hargeysa", "Kismaayo", "Muqdisho", "Baydhabo", "Muqdisho"),
            ("Waa kuma madaxweynaha Soomaaliya (2025)?", "Farmaajo", "Shariif", "Xasan Sheekh", "Cali Mahdi", "Xasan Sheekh"),
            ("Imisa gobol ayaa ka kooban Soomaaliya?", "12", "15", "18", "22", "18"),
            ("Calanka buluugga ah ee Soomaaliya waxaa naqshadeeyay?", "Sayidka", "Awale Liban", "Farmaajo", "Maxamed Cali", "Awale Liban"),
            ("Waa kee webiga ugu dheer Soomaaliya?", "Webiga Jubba", "Webiga Nile", "Webiga Doollo", "Webiga Shabelle", "Webiga Jubba"),
            ("Waa kuma halyaygii gobonimada Soomaaliya?", "Farmaajo", "Shariif", "Sayid Maxamed", "Cali Mahdi", "Sayid Maxamed"),
            ("Soomaaliya waxay xuduud la leedahay waddan kee?", "Sudan", "Chad", "Kenya", "Algeria", "Kenya"),
            ("Dekedda ugu weyn Soomaaliya waa?", "Berbera", "Kismaayo", "Mogadishu", "Hobyo", "Mogadishu"),
            ("Soomaaliya waxay ku taalaa qaaradda?", "Asia", "Africa", "Australia", "Europe", "Africa"),
            ("Soomaaliya waxa ay xorowday sannadkee?", "1969", "1960", "1955", "1975", "1960")
        ]
        c.executemany("INSERT INTO questions (question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?)", questions)

    conn.commit()
    conn.close()

# 🏠 Home
@app.route('/')
def home():
    return redirect('/login')

# 📝 Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect('/login')
        except:
            message = "Magacaas hore ayaa loo isticmaalay!"
        finally:
            conn.close()
    return render_template('register.html', message=message)

# 🔐 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password_input):
            session['user_id'] = user[0]
            return redirect('/welcome')

        message = "Username ama password waa qalad!"

    return render_template('login.html', message=message)

# 👋 Welcome Page
@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('welcome.html')

# 🚪 Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

# 🧠 Quiz Page
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    user_id = session['user_id']

    # Check if already took quiz
    c.execute("SELECT * FROM results WHERE user_id = ?", (user_id,))
    if c.fetchone():
        conn.close()
        return render_template('quiz.html', questions=[], message="Horay Baad Uqaaday Quizka!")

    if request.method == 'POST':
        score = 0
        c.execute("SELECT * FROM questions")
        questions = c.fetchall()
        for q in questions:
            user_answer = request.form.get(f'q{q[0]}')
            if user_answer == q[6]:
                score += 1

        c.execute("INSERT INTO results (user_id, score) VALUES (?, ?)", (user_id, score))
        conn.commit()
        conn.close()
        return redirect('/result')

    # GET
    c.execute("SELECT * FROM questions")
    questions = c.fetchall()
    conn.close()
    return render_template('quiz.html', questions=questions, message="")
# ✅ Result Page
@app.route('/result')
def result():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    user_id = session['user_id']

    c.execute("SELECT score FROM results WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return render_template('result.html', score=row[0], total=10)
    return "Ma jiraan natiijooyin!"




# 🧪 Optional: View how many questions are in DB
@app.route('/questions_count')
def questions_count():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM questions")
    count = c.fetchone()[0]
    conn.close()
    return f"Su'aalaha ku jira database-ka waa: {count}"

# Run
if __name__ == '__main__':
    init_db()
    app.run(debug=True)