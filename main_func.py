from flask import Flask, render_template, request, jsonify, redirect, url_for
import bcrypt
import psycopg2
from flask import request, jsonify
from flask_login import login_required, current_user
from flask_login import LoginManager
from flask_login import UserMixin

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

# Функция для подключения к базе данных
def connect_db():
    conn = psycopg2.connect(
        dbname="data",
        # password="",  # пароль не установлен, поэтому его можно оставить пустым
        host="localhost",  # если база данных находится на локальной машине
        port="5432"  # порт по умолчанию для PostgreSQL
    )
    return conn

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


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    print(username,password)
    # Генерация соли и хеширование пароля
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    salt = salt.decode('utf8')
    password_hash = hashed_password.decode('utf8')
    conn = connect_db()  # Открываем соединение
    cursor = conn.cursor()
    # Сохранение пользователя в базу данных
    cursor.execute("INSERT INTO users1 (username, password, salt) VALUES (%s, %s, %s)", (username, password_hash, salt))

    conn.commit()
    conn.close()
    print("Пользователь зарегистрирован")
    return jsonify({'message': 'Пользователь зарегистрирован'})

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

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

    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            print("ok login")
            # token = create_token(user[0], user[1])
            # print(token)
            return jsonify({'message': 'Пользователь зарегистрирован'})
    else:
        print("Неверные учетные данные")
        return jsonify({'message': 'Неверные учетные данные'}), 401


@login_manager.user_loader
def load_user(id):
    conn = connect_db()  # Открываем соединение
    cursor = conn.cursor()  # Создаем курсор

    # Получение информации о пользователе из базы данных
    cursor.execute("SELECT id, username, password, salt FROM users1 WHERE id = %s", (id,))

    user = cursor.fetchone()
    usr = User(user[0], user[1], user[2],)

    conn.close()
    # Например, предположим, что user_id это идентификатор пользователя
    return User.get(id)




# Маршрут для отображения данных из базы данных
@app.route('/')
def start_template():
    return render_template('login.html')

@app.route('/false')
def display_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
           SELECT emails3.device_id, emails3.subject, emails3.addr, emails3.alarm, emails3.temp, emails3.occurred, emails3.time, devices.comment
           FROM emails3
           LEFT JOIN devices ON devices.id = emails3.device_id
           WHERE emails3.s_active = %s
       ''', ('false',))
    data = cursor.fetchall()

    conn.close()
    return render_template('emails.html', data=data)



@app.route('/active')
def display_data1():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT emails3.device_id, emails3.subject, emails3.addr, emails3.alarm, emails3.temp, emails3.occurred, emails3.time, devices.comment
        FROM emails3
        LEFT JOIN devices ON devices.id = emails3.device_id
        WHERE emails3.s_active = %s
    ''', ('true',))

    data = cursor.fetchall()

    conn.close()
    return render_template('emails.html', data=data)

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

if __name__ == '__main__':
    app.run(debug=True)
