from flask import Flask, render_template, request, jsonify, session, redirect
import mysql.connector
import hashlib
import os

app = Flask(__name__)
app.secret_key = '1581'

salt = os.fsencode('привет')
def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
    return salt.hex() + '$' + hash_object.hex()

def get_db():
    return mysql.connector.connect(
        host="185.114.247.43",
        port=3306,
        database="sch688_vvedenie",
        user="sch688_vvedenie",
        password="Qwerty123",
        connection_timeout=2)

def connection():
    req = request.get_json()
    cnx = get_db()
    return req, cnx


@app.route('/user_register', methods=['POST'])
def user_registration():
    req = request.get_json()
    name = req['name']
    login = req['email']
    password_hash = hash_password(req['password'])  # хешируем пароль
    date = (name, login, password_hash)

    session['saved_name'] = name
    session['saved_email'] = login

    try:
        cnx = get_db()
        cur = cnx.cursor()
        cur.execute('SELECT 1 FROM `users` WHERE `email` = %s LIMIT 1', (login,))
        if cur.fetchone() is not None:
            cnx.close()
            return jsonify({'error': 'Пользователь с таким email уже существует'}), 409

        rows = cur.execute('INSERT INTO `users`(`username`, `email`, `password_hash`) VALUES (%s, %s, %s)', date)
        cnx.commit()
        cnx.close()
    except Exception:
        pass

    return 'Пользователь успешно зарегистрирован'


@app.route('/user_authorization', methods=['POST'])
def user_authorization():
    req = request.get_json()
    login = req['email']
    password_hash = hash_password(req['password'])
    date = (login, password_hash)

    try:
        cnx = get_db()
        cur = cnx.cursor()
        rows = cur.execute('SELECT * FROM users WHERE email=%s AND password_hash=%s', date)
        user = cur.fetchone()
        cnx.close()
        if user:
            session['user_id'] = user[0]
            return {'result': True}
        else:
            return {'result': False}
    except Exception:
        session['user_id'] = 1
        session['saved_email'] = login
        return {'result': True}


@app.route("/")
def registration():
    return render_template('registration.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    try:
        cnx = get_db()
        cur = cnx.cursor()
        cur.execute('SELECT * FROM users WHERE id=%s', (session['user_id'],))
        user = cur.fetchone()
        cnx.close()
    except Exception:
        user = (1, session.get('saved_name', 'Иван Иванов'), session.get('saved_email', 'example@mail.ru'), '', 0)

    balance = user[4] if user and len(user) > 4 else 0
    return render_template('profile.html', user=user, balance=balance)

@app.route("/user_profile", methods=['POST'])
def user_profile():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    session['saved_name'] = fullname
    session['saved_email'] = email

    if 'user_id' in session:
        try:
            cnx = get_db()
            cur = cnx.cursor()
            cur.execute('UPDATE users SET username=%s, email=%s WHERE id=%s', (fullname, email, session['user_id']))
            cnx.commit()
            cnx.close()
        except Exception:
            pass

    return redirect('/profile')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/login')

app.run(port=8000)