import sqlite3 as sq
import pathlib
from pathlib import Path


def check(login, domain):
    db = sq.connect(Path(pathlib.Path.home(), 'Desktop', 'ОИБ', 'Курсовой проект', 'KerberosProgram', 'client.db'))
    sql = db.cursor()

    request = '''SELECT * FROM clients WHERE LOGIN = ? AND DOMAIN = ?;'''
    info = (login, domain)

    sql.execute(request, info)
    value = sql.fetchall()
    if value:
        return value[0][4]
    else:
        return False

# def insert():
#     db = sq.connect(Path(pathlib.Path.home(), 'Desktop', 'ОИБ', 'Курсовой проект', 'KerberosProgram', 'client.db'))
#     sql = db.cursor()
#
#     inc = '''INSERT INTO clients (LOGIN, DOMAIN, PASSWORD, HASH_PASSWORD) VALUES (?, ?, ?, ?);'''
#     info_user = ('Stanislav', 'domain_main', 'Duat', '$2b$12$Tm2WtS851uQ.oU..kY2Eb.yUazI5iDmSq.ZVcgcydBImy0TU0.G4G')
#
#     sql.execute(inc, info_user)
#
#     db.commit()
#
#
# def start():
#     db = sq.connect(Path(pathlib.Path.home(), 'Desktop', 'ОИБ', 'Курсовой проект', 'KerberosProgram', 'client.db'))
#     sql = db.cursor()
#
#     sql.execute('''CREATE TABLE clients (
#         ID INTEGER PRIMARY KEY AUTOINCREMENT,
#         LOGIN TEXT NOT NULL,
#         DOMAIN TEXT NOT NULL,
#         PASSWORD TEXT NOT NULL,
#         HASH_PASSWORD TEXT NOT NULL
#     );''')
#
#     db.commit()
