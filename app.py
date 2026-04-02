from flask import Flask, render_template, request, jsonify, abort
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.config['DATABASE'] = 'demo.db'


def init_db():
    if not os.path.exists('demo.db'):
        conn = sqlite3.connect('demo.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
        ''')
        c.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')")
        c.execute("INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com')")
        c.execute("INSERT INTO posts (title, content, author_id) VALUES ('First Post', 'Hello Flask!', 1)")
        c.execute("INSERT INTO posts (title, content, author_id) VALUES ('Second Post', 'Flask is awesome!', 2)")
        conn.commit()
        conn.close()


def get_db():
    conn = sqlite3.connect('demo.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT posts.id, posts.title, posts.content, posts.created_at, users.name as author
        FROM posts LEFT JOIN users ON posts.author_id = users.id
        ORDER BY posts.created_at DESC
    ''')
    posts = c.fetchall()
    conn.close()
    return render_template('index.html', posts=posts, now=datetime.now())


@app.route('/users')
def list_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def get_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    if user is None:
        conn.close()
        abort(404)
    c.execute('SELECT * FROM posts WHERE author_id = ? ORDER BY created_at DESC', (user_id,))
    posts = c.fetchall()
    conn.close()
    return render_template('user_detail.html', user=user, posts=posts)


@app.route('/api/users', methods=['GET'])
def api_list_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name, email, created_at FROM users')
    users = c.fetchall()
    conn.close()
    return jsonify([dict(row) for row in users])


@app.route('/api/users', methods=['POST'])
def api_create_user():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'name and email are required'}), 400
    
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO users (name, email) VALUES (?, ?)', (data['name'], data['email']))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'id': user_id, 'name': data['name'], 'email': data['email']}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'email already exists'}), 409


@app.route('/api/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name, email, created_at FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user is None:
        return jsonify({'error': 'user not found'}), 404
    return jsonify(dict(user))


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'name and email are required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (data['name'], data['email'], user_id))
    if c.rowcount == 0:
        conn.close()
        return jsonify({'error': 'user not found'}), 404
    conn.commit()
    conn.close()
    return jsonify({'id': user_id, 'name': data['name'], 'email': data['email']})


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    if c.rowcount == 0:
        conn.close()
        return jsonify({'error': 'user not found'}), 404
    conn.commit()
    conn.close()
    return jsonify({'message': 'user deleted'}), 200


@app.route('/api/posts', methods=['GET'])
def api_list_posts():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT posts.id, posts.title, posts.content, posts.created_at, 
               users.name as author_name, users.id as author_id
        FROM posts LEFT JOIN users ON posts.author_id = users.id
        ORDER BY posts.created_at DESC
    ''')
    posts = c.fetchall()
    conn.close()
    return jsonify([dict(row) for row in posts])


@app.route('/api/posts', methods=['POST'])
def api_create_post():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data or 'author_id' not in data:
        return jsonify({'error': 'title, content and author_id are required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)', 
              (data['title'], data['content'], data['author_id']))
    post_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': post_id, 'title': data['title'], 'content': data['content']}), 201


@app.route('/about')
def about():
    return render_template('about.html', now=datetime.now())


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
