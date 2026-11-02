from flask import Flask, render_template, request, jsonify, session
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

def connection():
    req = request.get_json()
    cnx = mysql.connector.connect(
        host="185.114.247.43",
        port=3306,
        database="sch688_vvedenie",
        user="sch688_vvedenie",
        password="Qwerty123")
    return req, cnx


@app.route('/user_register', methods=['POST'])
def user_registration():
    req, cnx = connection()
    name = req['name']
    login = req['email']
    password_hash = hash_password(req['password'])  # хешируем пароль
    date = (name, login, password_hash)
    cur = cnx.cursor()

    cur.execute('SELECT 1 FROM `users` WHERE `email` = %s LIMIT 1', (login,))
    if cur.fetchone() is not None:
        cnx.close()
        return jsonify({'error': 'Пользователь с таким email уже существует'}), 409

    rows = cur.execute('INSERT INTO `users`(`username`, `email`, `password_hash`) VALUES (%s, %s, %s)', date)
    cnx.commit()
    cnx.close()

    return 'Пользователь успешно зарегистрирован'


@app.route('/user_authorization', methods=['POST'])
def user_authorization():
    req, cnx = connection()
    login = req['email']
    password_hash = hash_password(req['password'])
    date = (login, password_hash)
    cur = cnx.cursor()

    rows = cur.execute('SELECT * FROM users WHERE email=%s AND password_hash=%s', date)
    user = cur.fetchone()
    if user:
        session['user_id'] = user[0]
        cnx.close()
        return {'result': True}
    else:
        cnx.close()
        return {'result': False}


@app.route("/")
def registration():
    return render_template('registration.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/profile")
def profile():
    # user = 'Select...'.fetchone()
    # balance = 
    return render_template('profile.html', user=session['user_id'])

app.run(port=8000)