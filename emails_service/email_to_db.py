
import psycopg2
import imaplib
import email
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time
from datetime import datetime
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'cruds.json'
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
spreadsheet_id = os.environ.get('TABLE_ID')

def create_conn():
    try:
        conn = psycopg2.connect(
            dbname="alarmer_db",
            user= "flaks_app",
            password="qwerty",  # пароль не установлен, поэтому его можно оставить пустым
            host="db",  # если база данных находится на локальной машине
            port="5432"  # порт по умолчанию для PostgreSQL
        )
        return conn
    except psycopg2.Error as e:
        print('An error occurred:', str(e))
        time.sleep(20)
        return create_conn()

def create_table():
    try:
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS devices (
                        id SERIAL PRIMARY KEY,
                        subject TEXT NOT NULL,
                        device_name TEXT NOT NULL,
                        comment TEXT DEFAULT ' ',
                        time_text TEXT NOT NULL
                    )
                ''')
        print("fin")
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS emails (
                        id SERIAL PRIMARY KEY,
                        subject TEXT NOT NULL,
                        alarm TEXT NOT NULL,
                        addr TEXT NOT NULL,
                        occurred TEXT NOT NULL,
                        time TEXT NOT NULL,
                        s_active TEXT,
                        status TEXT DEFAULT ' ',
                        device_id INTEGER, 
                        FOREIGN KEY (device_id) REFERENCES devices(id)
                    )
                ''')
        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS block (
                                id SERIAL PRIMARY KEY,
                                subject TEXT NOT NULL,
                                device_id TEXT NOT NULL,
                                time TEXT NOT NULL
                            )
                        ''')
        conn.commit()
    except psycopg2.Error as e:
        print('An error occurred:', str(e))
        time.sleep(20)
        create_table()

conn = create_conn()
cursor = conn.cursor()
create_table()
def get_email_body(email_message):
    email_body = ""
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            email_body = part.as_string()
    email_array = extract_alarms(email_body)
    for val in email_array:
        time.sleep(1)
        extract_data(val)
    return


def extract_alarms(text):
    start_delimiter = 'Unit:'
    end_delimiter = '------------------------------------------------'
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
        alarm_start_index = text.find('EMS Alarm:')
        alarm_data = text[alarm_start_index:alarm_start_index + 25]
        alarm_list.insert(0, f"{alarm_data} \n {data}")
        index = end_index + len(end_delimiter)
    return alarm_list


def extract_data(string):
    data = {
        "ems": 'NONE',
        "alarm": 'NONE',
        "addr": 'NONE',
        "occurred": 'NONE',
        "clear": "false"
    }
    split_keywords = {
        "EMS Alarm: ": "ems",
        "--- ": "alarm",
        "GA1 - ": "alarm",
        "Generic: ": "addr",
        "Alarm occurred: ": "occurred",
        "Offline": "alarm",
        "Compressor": "alarm",
        "A20 ": "alarm",
        "A21 ": "alarm",
        "A45 ": "alarm",
        "I/O ": "alarm",
        "SsA ": "alarm",
        "Common": "alarm",
        "Comp ": "alarm",
        "Calibrate ": "alarm",
        "Standby": "alarm",
        "PoA ": "alarm",
        "Pc ": "alarm",
        "PoB ": "alarm",
        "Fan": "alarm",
        "Oil": "alarm",
        "IO": "alarm",
    }
    for keyword, key in split_keywords.items():
        split_string = string.split(keyword)
        if len(split_string) > 1:
            data[key] = split_string[1].split("\n")[0]
    split_string = string.split("Offline\n")
    if len(split_string) > 1:
        data["alarm"] = "OFFLINE"
        data["addr"] = split_string[1].split("\nAddr:")[0]
    if data["addr"] == "NONE":
        split_string = string.split("Addr: ")
        if len(split_string) > 1:
            data["addr"] = str(split_string[1].split("\n")[0])
    split_string = string.split("Alarm cleared")
    if len(split_string) > 1:
        data["clear"] = "true"

    email_data = {
        'subject': data['ems'],
        'alarm': data['alarm'],
        'addr': data['addr'],
        'occurred': data['occurred'],
        'time': datetime.now().strftime("%d/%m/%y %H:%M"),
        'clear': data['clear']
    }
    split_string = string.split("Test Alarm")
    if len(split_string) > 1:
        return test_counter(data)
    if data["clear"] == "true":
        delete_email_from_db(email_data)
        return delete_email_from_sheet(data)

    add_email_to_sheet(email_data)
    add_email_to_db(email_data)

def test_counter(data):
    add_block(data)
    try:
        cursor.execute("UPDATE block SET time = %s WHERE subject = %s AND device_id = %s",
                               (data['occurred'], data['ems'], data['addr']))
        conn.commit()
        print("Row in database updated.")
    except psycopg2.Error as e:
        print("An error occurred:", e)


def check_records():
        # Получаем текущее время
        current_time = datetime.now()

        # Выполняем запрос к базе данных
        cursor.execute("SELECT * FROM block")
        rows = cursor.fetchall()

        # Проходимся по каждой записи
        for row in rows:
            # Получаем время из записи
            print(row[3])
            record_time = datetime.strptime(row[3].strip(), '%d/%m/%y %H:%M')

            # Считаем разницу во времени
            time_difference = current_time - record_time

            email_data = {
                'subject': row[1],
                'alarm': f"offline block",
                'addr': row[2],
                'occurred': row[3],
                'time': datetime.now().strftime("%d/%m/%y %H:%M"),
                'clear': 'false'
            }
            # Если разница больше часа, выводим сообщение в консоль
            if time_difference.total_seconds() > 10800:
                add_email_to_db(email_data)
                add_email_to_sheet(email_data)
                print(f"Время записи отличается от текущего на более чем час: {row}")
            else:
                data = {
                    "ems": row[1],
                    "alarm": f"offline block",
                    "addr": row[2],
                    "occurred": row[3],
                    "clear": "false"
                }
                delete_email_from_db(email_data)
                delete_email_from_sheet(data)

def add_block(data):
    cursor.execute("SELECT * FROM block WHERE subject = %s AND device_id = %s",
                   (data['ems'], data['addr'],))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO block (subject, device_id,time) VALUES (%s, %s, %s)",
                       (data['ems'], data['addr'], data['occurred']))
        conn.commit()
        print(f"add device to table {data['addr']}")
        cursor.execute("SELECT * FROM devices WHERE subject = %s AND device_name = %s",
                       (data['ems'], data['addr'],))
        row = cursor.fetchone()
        return row[0]
    else:
        return row[0]
def add_device(email_data):
    cursor.execute("SELECT * FROM devices WHERE subject = %s AND device_name = %s",
                   (email_data['subject'], email_data['addr'],))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO devices (subject, device_name,time_text) VALUES (%s, %s, %s)",
            (email_data['subject'], email_data['addr'], email_data['time']))
        conn.commit()
        print(f"add device to table {email_data['addr']}")
        cursor.execute("SELECT * FROM devices WHERE subject = %s AND device_name = %s",
                       (email_data['subject'], email_data['addr'],))
        row = cursor.fetchone()
        return row[0]
    else:
        return row[0]




def add_email_to_sheet(email_data):
    sheet = service.spreadsheets()
    sheet_id = 0
    time.sleep(1)
    try:
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id, range='A:C').execute()
        values = result.get('values', [])
        for i in range(len(values)):
            if len(values[i]) >= 3 and values[i][0] == email_data['subject'] and values[i][1] == email_data['alarm'] and values[i][2] == email_data['addr']:
                return print("Duplicate of cell")
        body = {
            'values': [[
                email_data['subject'],
                email_data['alarm'],
                email_data['addr'],
                email_data['occurred'],
                email_data['time']
            ]]
        }
        result = sheet.values().append(
            spreadsheetId=spreadsheet_id, range='A:E',
            valueInputOption='USER_ENTERED', body=body).execute()
        return print(email_data)
    except Exception as e:
        print('An error occurred:', str(e))
        time.sleep(60)
        # Попытка повторного выполнения функции add_email_to_sheet
        add_email_to_sheet(email_data)


def delete_email_from_sheet(email_data):
    try:
        sheet = service.spreadsheets()
        sheet_id = 0
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id, range='A:E').execute()
        values = result.get('values', [])
        for i in range(len(values)):
            if len(values[i]) >= 3 and values[i][0] == email_data['ems'] and values[i][1] == email_data['alarm'] and \
                    values[i][2] == email_data['addr']:
                body = {
                    'requests': [
                        {
                            'deleteDimension': {
                                'range': {
                                    'sheetId': sheet_id,
                                    'dimension': 'ROWS',
                                    'startIndex': i,
                                    'endIndex': i + 1
                                }
                            }
                        }
                    ]
                }
                sheet.batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
                print("Email deleted from sheet. ", str(body))
                return True
        print("Email not found in sheet.")
        return False
    except Exception as e:
        print("An error occurred:", str(e))
        time.sleep(59)  # Пауза в 59 секунд
        delete_email_from_sheet(email_data)


def add_email_to_db(email_data):
    try:
        device_id = add_device(email_data)  # Добавляем информацию об устройстве и получаем его идентификатор
        cursor.execute("SELECT * FROM emails WHERE subject = %s AND alarm = %s AND addr = %s AND s_active = %s",
                       (email_data['subject'], email_data['alarm'], email_data['addr'], 'false'))
        row = cursor.fetchone()
        if row is not None:
               return print("duplicate")
        else:
            # Теперь добавляем запись об аварии, указывая идентификатор устройства
            cursor.execute("INSERT INTO emails (subject, alarm, addr, occurred, time, s_active, device_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (email_data['subject'], email_data['alarm'], email_data['addr'], email_data['occurred'],email_data['time'], email_data['clear'], device_id))
            conn.commit()
            cursor.execute("SELECT * FROM emails")
            row = cursor.fetchone()
            return print(f'db: {row}')
    except psycopg2.Error as e:
        print('An error occurred:', str(e))


def delete_email_from_db(email_data):
    try:
        add_device(email_data)
        cursor.execute("SELECT * FROM emails WHERE subject = %s AND alarm = %s AND addr = %s",
                       (email_data['subject'], email_data['alarm'], email_data['addr']))
        row = cursor.fetchone()
        if row is not None:
            cursor.execute("UPDATE emails SET s_active = true WHERE subject = %s AND alarm = %s AND addr = %s",
                           (email_data['subject'], email_data['alarm'], email_data['addr']))
            conn.commit()
            print("Row in database updated.")
        else:
            print("Email not found in database.")
    except psycopg2.Error as e:
        print("An error occurred:", e)



def disconnect_imap_connection(imap_conn):
    try:
        imap_conn.logout()
        print("IMAP connection successfully disconnected.")
    except Exception as e:
        print(f"Error occurred while disconnecting IMAP connection: {e}")





def connect_imap_server():
    imap_host =os.environ.get('ML_HOST')
    mail = imaplib.IMAP4_SSL(imap_host)
    email_adress = os.environ.get('ML_USER')
    email_pass = os.environ.get('ML_PASSWORD')
    mail.login(email_adress, email_pass)
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
            time.sleep(10)
            check_records()
        except imaplib.IMAP4_SSL.abort as e:
            print(f'IMAP connection aborted: {e}')
            # Обработка возникшего исключения (например, переподключение)



        time.sleep(20)

process_emails()
