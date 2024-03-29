import time

from flask import render_template, request, jsonify, redirect, url_for
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user

import psycopg2
from flask import request, jsonify

from flask_login import LoginManager
from flask_login import UserMixin

from flask import Flask

app = Flask(__name__)
app.secret_key = 'scooby'
login_manager = LoginManager()
login_manager.init_app(app)

    # Функция для подключения к базе данных
def connect_db():
     conn = psycopg2.connect(
            dbname="alarmer_db",
            user="flaks_app",
            password="qwerty",  # пароль не установлен, поэтому его можно оставить пустым
            host="db",  # если база данных находится на локальной машине
            port="5432"  # порт по умолчанию для PostgreSQL
        )
     return conn
def create_table():
        try:
            conn = connect_db()
            cursor = conn.cursor()
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS users1 (
                id serial PRIMARY KEY,
                username VARCHAR (5000) UNIQUE NOT NULL,
                password VARCHAR (1000) NOT NULL,
                salt VARCHAR (500) NOT NULL
            );
            '''
            cursor.execute(create_table_query)
            conn.commit()
        except psycopg2.Error as e:
            time.sleep(10)
            print('An error occurred:', str(e))
            create_table()


create_table()
"""
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    salt = "salt"
    print(username,password)
    conn = connect_db()  # Открываем соединение
    cursor = conn.cursor()
    # Сохранение пользователя в базу данных
    cursor.execute("INSERT INTO users1 (username, password, salt) VALUES (%s, %s, %s)", (username, password, salt))
    conn.commit()
    conn.close()
    print("Пользователь зарегистрирован")
    return jsonify({'message': 'Пользователь зарегистрирован'})
"""
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, salt FROM users1 WHERE id = %s", (id,))
    user = cursor.fetchone()
    conn.close()
    return User(user[0], user[1], user[2]) if user else None

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    print(username, password)

    conn = connect_db()  # Открываем соединение
    cursor = conn.cursor()  # Создаем курсор

    # Получение информации о пользователе из базы данных
    cursor.execute("SELECT id, username, password, salt FROM users1 WHERE username = %s", (username,))
    user = cursor.fetchone()

    print(user)

    conn.close()  # Закрываем соединение

    if user and password == user[2]:
            print("ok login")
            # token = create_token(user[0], user[1])
            # print(token)
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            return jsonify({'message': 'Пользователь зарегистрирован'})
    else:
        print("Неверные учетные данные")
        return jsonify({'message': 'Неверные учетные данные'}), 401







# Маршрут для отображения данных из базы данных
@app.route('/')
def start_template():
    return render_template('login.html')
@app.route('/test')
def test_template():
    return render_template('test.html')
@app.route('/false')
@login_required
def display_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
           SELECT emails.device_id, emails.subject, emails.addr, emails.alarm, emails.occurred, emails.time, devices.comment, emails.status,emails.s_active
           FROM emails
           LEFT JOIN devices ON devices.id = emails.device_id
           WHERE emails.s_active = %s
       ''', ('true',))
    data = cursor.fetchall()
    print(data)
    conn.close()
    return render_template('false.html', res=data)



@app.route('/active')
@login_required
def display_data1():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT emails.device_id, emails.subject, emails.addr, emails.alarm, emails.occurred, emails.time,devices.comment, emails.status
        FROM emails
        LEFT JOIN devices ON devices.id = emails.device_id
        WHERE emails.s_active = %s
    ''', ('false',))

    data = cursor.fetchall()
    print(data)

    conn.close()

    return render_template('emails.html', res=data)

@app.route('/devices')
def display_data2():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices")
    data = cursor.fetchall()

    conn.close()
    return render_template('devices.html', data=data)


@app.route('/update-email', methods=['POST'])
def update_email():
    data = request.json  # Получаем данные из POST запроса, отправленного из вашего веб-приложения
    id = data['id']
    comment = data['newText']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE devices SET comment = %s WHERE id = %s", (comment, id))
    conn.commit()

    conn.close()

    return jsonify({'message': 'Email updated successfully'})

@app.route('/update-status', methods=['POST'])
def update_status():
    data = request.json
    id = data['id']
    comment = data['selectedValue']
    print(id,comment)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE emails SET status = %s WHERE device_id = %s AND s_active = %s", (comment, id, 'false'))

    conn.commit()
    conn.close()
    return jsonify({'message': 'status updated successfully'})

@app.route('/logout')
@login_required
def logout():
    logout_user()










