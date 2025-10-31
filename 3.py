"""
Minimal Todo app with Register / Login / Logout (SQLite)
Run:
  pip install Flask
  python todo_auth.py
Open http://127.0.0.1:5000
"""
from flask import Flask, request, redirect, url_for, render_template_string, session, flash, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

DB_PATH = 'todo.db'
SECRET_KEY = os.environ.get('TODO_SECRET', 'dev-secret-change-me')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DATABASE'] = DB_PATH

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    ''')
    db.commit()

with app.app_context():
    init_db()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Iltimos avval tizimga kiring.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if 'user_id' not in session:
        return None
    db = get_db()
    return db.execute('SELECT id, username FROM users WHERE id = ?', (session['user_id'],)).fetchone()

BASE_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Todo Auth</title>
  <style>
    body{font-family:Arial, sans-serif;max-width:800px;margin:20px auto}
    .nav{margin-bottom:12px}
    .flash{padding:8px;background:#fffbdd;margin-bottom:10px}
    .todo{display:flex;gap:8px;align-items:center}
    .done{text-decoration:line-through;color:gray}
    form.inline{display:inline}
  </style>
</head>
<body>
  <div class="nav">
    {% if user %}
      Salom, <strong>{{ user['username'] }}</strong> | <a href="{{ url_for('todos') }}">Todos</a> | <a href="{{ url_for('logout') }}">Chiqish</a>
    {% else %}
      <a href="{{ url_for('index') }}">Bosh sahifa</a> | <a href="{{ url_for('register') }}">Ro'yxatdan o'tish</a> | <a href="{{ url_for('login') }}">Kirish</a>
    {% endif %}
  </div>
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, msg in messages %}
      <div class="flash">{{ msg }}</div>
    {% endfor %}
  {% endwith %}
  {% block body %}{% endblock %}
</body>
</html>
"""

INDEX_HTML = """
{% extends 'base' %}
{% block body %}
  <h2>Bosh sahifa</h2>
  <p>Oddiy todo + auth misoli.</p>
{% endblock %}
"""

REGISTER_HTML = """
{% extends 'base' %}
{% block body %}
  <h2>Ro'yxatdan o'tish</h2>
  <form method="post">
    <label>Username:<br><input name="username" required></label><br><br>
    <label>Password:<br><input name="password" type="password" required></label><br><br>
    <button type="submit">Ro'yxatdan o'tish</button>
  </form>
{% endblock %}
"""

LOGIN_HTML = """
{% extends 'base' %}
{% block body %}
  <h2>Kirish</h2>
  <form method="post">
    <label>Username:<br><input name="username" required></label><br><br>
    <label>Password:<br><input name="password" type="password" required></label><br><br>
    <input type="hidden" name="next" value="{{ request.args.get('next') or request.form.get('next') or '' }}">
    <button type="submit">Kirish</button>
  </form>
{% endblock %}
"""

TODOS_HTML = """
{% extends 'base' %}
{% block body %}
  <h2>My Todos</h2>
  <form method="post" action="{{ url_for('add_todo') }}">
    <input name="content" placeholder="Yangi todo" required>
    <button type="submit">Qo'shish</button>
  </form>
  <ul>
    {% for t in todos %}
      <li class="todo">
        <span class="{% if t['done'] %}done{% endif %}">{{ t['content'] }}</span>
        <form class="inline" method="post" action="{{ url_for('toggle_todo', todo_id=t['id']) }}">
          <button type="submit">{% if t['done'] %}Un-done{% else %}Done{% endif %}</button>
        </form>
        <form class="inline" method="post" action="{{ url_for('delete_todo', todo_id=t['id']) }}">
          <button type="submit">Delete</button>
        </form>
      </li>
    {% endfor %}
  </ul>
{% endblock %}
"""

def render_with_base(body_template, **ctx):
    return render_template_string(BASE_HTML + body_template, **ctx)

@app.route('/')
def index():
    user = get_current_user()
    return render_with_base(INDEX_HTML, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash("Iltimos barcha maydonlarni to'ldiring.", 'warning')
            return redirect(url_for('register'))
        db = get_db()
        try:
            pw_hash = generate_password_hash(password)
            db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, pw_hash))
            db.commit()
            flash("Ro'yxatdan muvaffaqiyatli o'tdingiz. Endi tizimga kiring.", 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Bu username allaqachon mavjud.', 'warning')
            return redirect(url_for('register'))
    return render_with_base(REGISTER_HTML, user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        next_url = request.form.get('next') or request.args.get('next') or url_for('todos')
        db = get_db()
        row = db.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,)).fetchone()
        if row and check_password_hash(row['password_hash'], password):
            session.clear()
            session['user_id'] = row['id']
            flash('Tizimga muvaffaqiyatli kirdingiz.', 'success')
            return redirect(next_url)
        flash('Username yoki parol xato.', 'warning')
        return redirect(url_for('login'))
    return render_with_base(LOGIN_HTML, user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('Siz tizimdan chiqdingiz.', 'success')
    return redirect(url_for('index'))

# --------- Todos ----------
@app.route('/todos')
@login_required
def todos():
    user = get_current_user()
    db = get_db()
    todos = db.execute('SELECT id, content, done FROM todos WHERE user_id = ? ORDER BY created_at DESC', (user['id'],)).fetchall()
    return render_with_base(TODOS_HTML, user=user, todos=todos)

@app.route('/todos/add', methods=['POST'])
@login_required
def add_todo():
    user = get_current_user()
    content = request.form['content'].strip()
    if content:
        db = get_db()
        db.execute('INSERT INTO todos (user_id, content) VALUES (?, ?)', (user['id'], content))
        db.commit()
        flash(\"Todo qo'shildi.\", 'success')
    return redirect(url_for('todos'))

@app.route('/todos/<int:todo_id>/toggle', methods=['POST'])
@login_required
def toggle_todo(todo_id):
    user = get_current_user()
    db = get_db()
    row = db.execute('SELECT id, done FROM todos WHERE id = ? AND user_id = ?', (todo_id, user['id'])).fetchone()
    if row:
        new_done = 0 if row['done'] else 1
        db.execute('UPDATE todos SET done = ? WHERE id = ?', (new_done, todo_id))
        db.commit()
    return redirect(url_for('todos'))

@app.route('/todos/<int:todo_id>/delete', methods=['POST'])
@login_required
def delete_todo(todo_id):
    user = get_current_user()
    db = get_db()
    db.execute('DELETE FROM todos WHERE id = ? AND user_id = ?', (todo_id, user['id']))
    db.commit()
    flash(\"Todo o'chirildi.\", 'success')
    return redirect(url_for('todos'))

if __name__ == '__main__':
    app.run(debug=True)