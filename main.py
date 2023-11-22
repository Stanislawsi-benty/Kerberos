from datetime import datetime

import database
from hash import *
from enryption.encrypt import *


def get_time():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    return current_time


class KeyDistributionCenter:
    def __init__(self):
        self.master_key_kdc = 'Gashkoff'
        self.session_key = 'Sergeevich'
        self.time_now = get_time()
        self.server_name = 'Anubis'
        self.client_server_key = 'Osiris'
        self.longTime_serverKey = 'Tutankhamen'
        print(f"{'-' * 100} KDC активен {'-' * 100}")
        print(f"Время на KDC: {self.time_now}")

    def auth(self, login_client, domain_client, time_client):
        print(f"\nАутентификация пользователя...\n\nЛогин: {login_client}\n"
              f"Домен клиента: {domain_client}\nЗашифрованное время: {time_client}")

        key = database.check(login_client, domain_client)

        if key:
            right_time = decrypt(time_client, key)
            print(f"Расшифрованное время: {right_time}\n")
            if len(self.time_now.split(':')) == len(right_time.split(':')):
                if (int(self.time_now.split(':')[1]) - 2) <= int(right_time.split(':')[1]) <= (
                        int(self.time_now.split(':')[1]) + 2):
                    print(f"\nПользователь аутентифицирован!\n")
                    self.TGT(login_client, right_time, key)
                else:
                    print(f"{'!' * 100} РАСХОЖДЕНИЕ ВО ВРЕМЕНИ {'!' * 100}")
                    exit()

            else:
                print(f"{'!' * 100} НЕВЕРНЫЙ ПАРОЛЬ {'!' * 100}")
                exit()

        else:
            print(f"{'!' * 100} ПОЛЬЗОВАТЕЛЬ НЕ ЗАРЕГИСТРИРОВАН {'!' * 100}")
            exit()

    def TGT(self, login_client, time_client, client_key):
        print("Передача клиенту Ticket Granting Ticket\n\n")
        emk_ks = encrypt(self.session_key, self.master_key_kdc)
        emk_login = encrypt(login_client, self.master_key_kdc)
        emk_TTL = encrypt('24', self.master_key_kdc)
        eh_ks = encrypt(self.session_key, client_key)
        eh_T = encrypt(time_client, client_key)
        ticket = [emk_ks, emk_login, emk_TTL, eh_ks, eh_T]
        user.accept_TGT(ticket)

    def check_TGT(self, Ticket_Granting_Ticket, ks_T, login_client, domain_client):
        key = database.check(login_client, domain_client)
        print("\nПолучен Ticket Granting Ticket и его время отправки от Клиента:")
        key_session_master = decrypt(Ticket_Granting_Ticket[0], self.master_key_kdc)
        login_client_master = decrypt(Ticket_Granting_Ticket[1], self.master_key_kdc)
        TTL = decrypt(Ticket_Granting_Ticket[2], self.master_key_kdc)
        key_session_client = decrypt(Ticket_Granting_Ticket[3], key)
        time_client = decrypt(Ticket_Granting_Ticket[4], key)

        request_time = decrypt(ks_T, self.session_key)
        print(f"\tСессионный ключ(мастер): {key_session_master}\n\tЛогин клиента(мастер): {login_client_master}\n\t"
              f"Время жизни(мастер): {TTL}\n\tСессионный ключ(хеш): {key_session_client}\n\t"
              f"Время клиента(хеш): {time_client}")
        print(f"\tВремя отправки Ticket Granting Ticket на Key Distribution Center: {request_time}")

        if key_session_master == self.session_key and login_client_master == login_client:
            self.TGS_c(login_client, time_client, TTL)
        else:
            print(f"{'!' * 100} Ticket Granting Ticket НЕВЕРНЫЙ {'!' * 100}")
            exit()

    def TGS_c(self, login_s, Time, TTL):
        """Формирование TGS"""
        tgs_open = [login_s, self.server_name, Time, TTL, self.client_server_key]
        tgs_close = [encrypt(i, self.session_key) for i in tgs_open]
        print("\nTicket Granting Server для клиента зашифрован")
        """Формирование TGSs"""
        tgs_s_serverKey = [encrypt(i, self.longTime_serverKey) for i in tgs_open]
        tgs_s_serverKey_sessionKey = [encrypt(i, self.session_key) for i in tgs_s_serverKey]
        print("\nTicket Granting Server_c для клиента зашифрован\n")

        print("Передан Ticket Granting Ticket_c от Key Distribution Center на Клиент\n\n")
        user.accept_TGS_c(tgs_close, tgs_s_serverKey_sessionKey, self.session_key)


class Client:
    def __init__(self, login_client, password_client, domain_client, time_client):
        print(f"{'-' * 100} Client активен {'-' * 100}")
        self.login = login_client
        self.password = password_client
        self.domain = domain_client
        self.time = time_client

        self.hash = to_hash(password_client)

        print(f"Инициализация пользователя...\n")
        print(
            f"Логин: {self.login}\nПароль: {self.password}\nДомен клиента: {self.domain}\nВремя запроса: {self.time}\n"
            f"Хеш-пароль: {self.hash}")

    def to_KDC(self):
        print(), print("Передача запроса от Клиента на Key Distribution Center")
        [print() for _ in range(2)]
        encrypt_time = encrypt(self.time, self.hash)
        Key_DC = KeyDistributionCenter()
        Key_DC.auth(self.login, self.domain, encrypt_time)

    def accept_TGT(self, data):
        print(f"{'-' * 100} Client {'-' * 100}")
        print("Получен Ticket Granting Ticket от Key Distribution Center:")
        print(f"\tСессионный ключ(мастер): {data[0]}\n\tЛогин(мастер): {data[1]}\n\tВремя жизни(мастер): {data[2]}\n"
              f"\tСессионный ключ(хеш): {decrypt(data[3], self.hash)}\n\tКлиентское время(хеш): "
              f"{decrypt(data[4], self.hash)}\n\n")
        print("Передача на Key Distribution Center Ticket Granting Ticket и время отправки\n\n")
        Key_DC = KeyDistributionCenter()
        Key_DC.check_TGT(data, encrypt(get_time(), decrypt(data[3], self.hash)), self.login, self.domain)

    def accept_TGS_c(self, TGS, TGS_s, key_session):
        print(f"{'-' * 100} Client {'-' * 100}")
        print("Получен Ticket Granting Ticket_c от Key Distribution Center:\n")
        TGS_open = [decrypt(i, key_session) for i in TGS]
        TGS_s_non_open = [decrypt(i, key_session) for i in TGS_s]
        print(f"Ticket Granting Server:\n\tЛогин: {TGS_open[0]}\n\tИмя сервера: {TGS_open[1]}\n\tВремя запроса: "
              f"{TGS_open[2]}\n\tВремя жизни: {TGS_open[3]}\n\tСеансовый ключ(клиент-сервер): {TGS_open[4]}\n\n")
        print(f"Ticket Granting Server_c:\n\tЛогин: {TGS_s_non_open[0]}\n\tИмя сервера: {TGS_s_non_open[1]}\n\t"
              f"Время запроса: {TGS_s_non_open[2]}\n\tВремя жизни: {TGS_s_non_open[3]}\n\t"
              f"Сеансовый ключ(клиент-сервер): {TGS_s_non_open[4]}\n")
        print("Передача времени и Ticket Granting Server на сервер-узел\n\n")

        time_clientServer = encrypt(get_time(), TGS_open[4])
        self.send_TGS_to_server(time_clientServer, TGS_s_non_open)

    @staticmethod
    def send_TGS_to_server(time, TGS_c):
        internet_knot = Server()
        internet_knot.auth_client(time, TGS_c)


class Server:
    def __init__(self):
        print(f"{'-' * 100} Server активен {'-' * 100}")
        print("Авторизация клиента...\n")
        self.server_name = 'Anubis'
        self.client_server_key = 'Osiris'
        self.longTime_serverKey = 'Tutankhamen'

    def auth_client(self, time, TGS_c):
        print("Получено Время и Ticket Granting Server от клиента\n")
        print(f"Время запроса: {decrypt(time, self.client_server_key)}\n")
        print(f"Ticket Granting Server:\n\tЛогин пользователя: {decrypt(TGS_c[0], self.longTime_serverKey)}\n\t"
              f"Имя сервера: {decrypt(TGS_c[1], self.longTime_serverKey)}\n\tВремя: "
              f"{decrypt(TGS_c[2], self.longTime_serverKey)}\n\tВремя жизни подключения: "
              f"{decrypt(TGS_c[3], self.longTime_serverKey)}\n\tСеансовый ключ(клиент-сервер): "
              f"{decrypt(TGS_c[4], self.longTime_serverKey)}\n")

        print(f"{'~' * 100} УСПЕШНОЕ ПОДКЛЮЧЕНИЕ! {'~' * 100}")


if __name__ == '__main__':
    login, password, domain = input("Введите логин: "), input("Введите пароль: "), input("Введите домен: ")
    [print() for _ in range(2)]

    user = Client(login, password, domain, get_time())
    user.to_KDC()
