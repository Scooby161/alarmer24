import imaplib
import email
import time
import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    dbname="data",
    # password="",  # пароль не установлен, поэтому его можно оставить пустым
    host="localhost",  # если база данных находится на локальной машине
    port="5432"  # порт по умолчанию для PostgreSQL
)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id SERIAL PRIMARY KEY,
        device_name TEXT NOT NULL,
        comment TEXT NOT NULL,
        time TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS emails3 (
        id SERIAL PRIMARY KEY,
        subject TEXT NOT NULL,
        alarm TEXT NOT NULL,
        addr TEXT NOT NULL,
        temp TEXT NOT NULL,
        occurred TEXT NOT NULL,
        time TEXT NOT NULL,
        s_active TEXT NOT NULL,
        device_id INTEGER,  -- Внешний ключ, ссылается на id в таблице devices
        FOREIGN KEY (device_id) REFERENCES devices(id)
    )
''')

def get_email_body(email_message):
    email_body = ""
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            email_body = part.as_string()
        extract_data(email_body)
    return


def extract_alarms(text):
    start_delimiter = 'RS1- '
    end_delimiter = 'MasterDefrost:'
    alarm_list = []
    index = 0
    while True:
        start_index = text.find(start_delimiter, index)
        if start_index == -1:
            break
        end_index = text.find(end_delimiter, start_index)
        if end_index == -1:
            break
        data = text[start_index:end_index]
        alarm_start_index = text.find('XWEBEVO')
        alarm_data = text[alarm_start_index:alarm_start_index + 25]
        alarm_list.insert(0, f"{alarm_data} \n {data}")
        index = end_index + len(end_delimiter)
    return alarm_list

def add_device(email_data):
    cursor.execute("SELECT * FROM devices WHERE subject = %s AND device_name = %s",
                   (email_data['subject'], email_data['addr'],))
    row = cursor.fetchone()
    if row is None:
        print(f"add device to table {email_data}")
        cursor.execute(
            "INSERT INTO devices (subject, device_name,comment,time) VALUES (%s, %s, %s, %s)",
            (email_data['subject'], email_data['addr'], 'test', email_data['time']))
    else:
        return row[0]
    conn.commit()

def add_comment():
    print("add add_comment()")
def extract_data(string):
    data = {
        "ems": 'NONE',
        "alarm": 'NONE',
        "addr": 'NONE',
        "occurred": 'NONE',
        "temp" : 'NONE',
        "exit" : 'true',
        "clear" : False,
    }
    split_keywords = {
        "XWEBEVO ": "ems",
        "START|": "occurred",
        "XM679K" : "alarm",
        "XM669K": "alarm",
        "|RS1-": "addr",
        "|RS2 -": "addr",
        "Regul. Probe: ": "temp",
    }
    for keyword, key in split_keywords.items():
        split_string = string.split(keyword)
        if len(split_string) > 1:
            if key == 'alarm':
                data[key] = split_string[1].split( )[0]
            elif key == 'temp':
                data[key] = split_string[1].split("=")[0]
            else:
                data[key] = split_string[1].split("|")[0]
    split_string = string.split("STOP")
    if len(split_string) > 1:
        data["clear"] = "true"
    email_data = {
        'subject': data['ems'],
        'alarm': data['alarm'],
        'addr': data['addr'],
        'temp': data['temp'],
        'occurred': data['occurred'],
        'exit': data['exit'],
        'time': datetime.now().strftime("%d/%m/%y %H:%M")
    }
    if email_data['subject'] == 'NONE':
        return False
    if data["clear"] == "true":
        return delete_email_from_sheet(email_data)
    add_email_to_sheet(email_data)



def add_email_to_sheet(email_data):
    try:
        device_id = add_device(email_data)  # Добавляем информацию об устройстве и получаем его идентификатор
        cursor.execute("SELECT * FROM emails3 WHERE subject = %s AND alarm = %s AND addr = %s AND temp != %s",
                       (email_data['subject'], email_data['alarm'], email_data['addr'], email_data['temp']))
        row = cursor.fetchone()
        if row is not None:
            return update_email_in_sheet(email_data, device_id)  # Передаем идентификатор устройства для обновления записи
        cursor.execute("SELECT * FROM emails3 WHERE subject = %s AND alarm = %s AND addr = %s AND temp = %s AND s_active = %s",
                       (email_data['subject'], email_data['alarm'], email_data['addr'], email_data['temp'], 'true'))
        row = cursor.fetchone()
        if row is not None:
               return print("duplicate")
        else:
            # Теперь добавляем запись об аварии, указывая идентификатор устройства
            cursor.execute("INSERT INTO emails3 (subject, alarm, addr, temp, occurred, time, s_active, device_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (email_data['subject'], email_data['alarm'], email_data['addr'], email_data['temp'], email_data['occurred'], email_data['time'], email_data['exit'], device_id))
            conn.commit()
            return print(email_data)
    except Exception as e:
        print('An error occurred:', str(e))


def update_email_in_sheet(email_data):
    try:
        cursor.execute("SELECT * FROM emails3 WHERE subject = %s AND alarm = %s AND addr = %s",
                       (email_data['subject'], email_data['alarm'], email_data['addr']))
        row = cursor.fetchone()
        if row is not None and row[3] != email_data['temp']:
            cursor.execute("UPDATE emails3 SET temp = %s, occurred = %s, time = %s WHERE subject = %s AND alarm = %s AND addr = %s",
                           (email_data['temp'], email_data['occurred'], email_data['time'], email_data['subject'], email_data['alarm'], email_data['addr']))
            conn.commit()
            print("Email updated in database.")
        else:
            print("Email not found in database.")
    except Exception as e:
        print("An error occurred:", e)

def delete_email_from_sheet(email_data):
    try:
        add_device(email_data)
        cursor.execute("SELECT * FROM emails3 WHERE subject = %s AND alarm = %s AND addr = %s",
                       (email_data['subject'], email_data['alarm'], email_data['addr']))
        row = cursor.fetchone()
        if row is not None:
            cursor.execute("UPDATE emails3 SET s_active = false WHERE subject = %s AND alarm = %s AND addr = %s",
                           (email_data['subject'], email_data['alarm'], email_data['addr']))
            conn.commit()
            print("Row in database updated.")
        else:
            print("Email not found in database.")
    except Exception as e:
        print("An error occurred:", e)


def disconnect_imap_connection(imap_conn):
    try:
        imap_conn.logout()
        print("IMAP connection successfully disconnected.")
    except Exception as e:
        print(f"Error occurred while disconnecting IMAP connection:1 {e}")





def connect_imap_server():
    mail = imaplib.IMAP4_SSL('imap.mail.ru')
    mail.login('sm1@es-company.ru', 'PjNc2325YD4N7bd2cLqh')
    return mail


def get_unread_emails(mail):
    mail.select('inbox')
    result, data = mail.search(None, 'UNSEEN')
    return data[0].split()

def process_emails():
    while True:
        try:
            mail = connect_imap_server()
            unread_emails = get_unread_emails(mail)
            for email_id in unread_emails:
                result, data = mail.fetch(email_id, '(RFC822)')
                raw_email = data[0][1]

                email_message = email.message_from_bytes(raw_email)

                get_email_body(email_message)
            disconnect_imap_connection(mail)

            time.sleep(120)

        except imaplib.IMAP4_SSL.abort as e:
            print(f'IMAP connection aborted: {e}')
            # Обработка возникшего исключения (например, переподключение)


        except Exception as e:
            print(f"Error occurred while disconnecting IMAP connection: {e}")
        time.sleep(20)


process_emails()