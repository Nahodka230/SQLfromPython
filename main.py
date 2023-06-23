#from nis import match

import psycopg2
class Client:
    def __init__(self):
        self.first_name = input('Введите имя: ')
        self.last_name = input('Введите фамилию: ')
        self.email = input('Введите e-mail: ')
    def add_client(self,conn):
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client(first_name, last_name, email) VALUES (%s, %s, %s) RETURNING client_id;
            """, (self.first_name, self.last_name, self.email))
            id = cur.fetchone()[0]
            print('Клиент добавлен')
            return id

    def find_client(self, conn):
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT client_id FROM client WHERE first_name = %s AND last_name = %s AND email = %s;
                        """, (self.first_name, self.last_name, self.email))
            conn.commit()
            if cur.rowcount > 1:
                print(cur.fetchone())
            else:
                if cur.rowcount == 1:
                    print(cur.fetchone())
                    return cur.fetchone()[0]
                else:
                    return 'None'
def create_db(conn):

        with conn.cursor() as cur:
            # создание таблиц
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS client(
                        client_id SERIAL PRIMARY KEY,
                        first_name VARCHAR(40) NOT NULL,
                        last_name  VARCHAR(40),
                        email VARCHAR(40)
                    );
                    """)
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS phone_number(
                        id SERIAL PRIMARY KEY,
                        phones VARCHAR(20) NOT NULL,
                        client_id INTEGER NOT NULL REFERENCES client(client_id)
                    );
                    """)
            conn.commit()  # фиксируем в БД

def add_phones(conn, id):
    phones = input('Введите номер телефона клиента:')
    with conn.cursor() as cur:
        cur.execute("""
                        INSERT INTO phone_number(phones, client_id) VALUES (%s, %s) RETURNING phones, client_id;
                        """, (phones, id))
        conn.commit()
        print('Номер телефона добавлен.')

def change_client(conn, id, first_name=None, last_name=None, email=None):
    with conn.cursor() as cur:
        cur.execute("""
                        UPDATE client SET first_name = %s, last_name = %s, email = %s WHERE client_id = %s;
                        """, (first_name, last_name, email, id))
        conn.commit()
        print('Данные о клиенте изменены')
        cur.execute("""
                                SELECT phones FROM phone_number WHERE client_id = %s;
                                """, (id,))
        print( 'Для данного клиента найдены следующие номера телефонов: ', cur.fetchall())
        chph = input(' \n Введите номер телефона, который хотите заменить или введите N для отмены редактирования номера телефона: ')
        if chph == 'N':
            exit()
        else:
            cur.execute("""
                           SELECT phones FROM phone_number WHERE phones = %s;
                           """, (chph,))
            conn.commit()
            if cur.rowcount !=0:
                new_phones = input('Введите новый номер телефона: ')
                cur.execute("""
                                    UPDATE phone_number SET phones = %s WHERE phones=%s ;
                                    """, (new_phones, chph))
                conn.commit()
                print('Номер телефона изменен')
            else:
                print('Номер телефона введен неверно.')

def del_phones(conn, id_client):
    with conn.cursor() as cur:
        cur.execute("""SELECT phones FROM phone_number WHERE client_id = %s;
                       """, (id_client,))
        print('Для данного клиента найдены следующие номера телефонов: ', cur.fetchall())
        delph = input(' \n Введите номер телефона, который хотите удалить: ')
        cur.execute("""SELECT phones FROM phone_number WHERE phones = %s;
                        """, (delph,))
        conn.commit()
        if cur.rowcount != 0:
            cur.execute("""DELETE FROM  phone_number WHERE phones=%s;
                        """, (delph,))
            conn.commit()
            print('Номер телефона удален')
        else:
            print('Номер телефона введен неверно.')
def del_client(conn, id):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM  phone_number WHERE client_id=%s;
                                """, (id,))
        cur.execute("""DELETE FROM  client WHERE client_id=%s;
                                        """, (id,))
        conn.commit()
        print('Данные о клиенте удалены')
def find_info_client(conn, first_name, last_name, email, phone):
    with conn.cursor() as cur:
        cur.execute("""SELECT c.client_id, c.first_name, c.last_name, c.email, p.phones FROM client c
                        JOIN phone_number p ON c.client_id = p.client_id WHERE c.first_name LIKE %s AND c.last_name LIKE %s AND c.email  LIKE %s AND p.phones  LIKE  %s;
                        """, (first_name,last_name,email,phone))
        print(cur.fetchall())

with psycopg2.connect(database="client", user="postgres", password="230105") as conn:
    create_db(conn)
    f = input('Выберите действие: '
              '\n 1 - Добавить нового клиента '
              '\n 2 - Изменить/удалить данные о существующем клиенте (в том числе телефон)'
              '\n 3 - Найти клиента \n')
    match f:
        case '1':
            New_client = Client()
            id = New_client.add_client(conn)
            f = input ('Добавить телефон? Y/N \n')
            while f == 'Y':
                add_phones(conn, id)
                f = input ('Добавить телефон? Y/N \n')

        case '2':
            Edit_client = Client()
            id = Edit_client.find_client(conn)
            if id != 'None':
                ef = input('Выберите действие:'
                      '\n1-добавить телефон'
                      '\n2-изменить данные о клиенте'
                      '\n3-удалить телефон'
                      '\n4-удалить клиента\n'
                      )
                match ef:
                    case '1':
                        add_phones(conn, id)
                    case '2':
                        print('Введите новые данные клиента: \n')
                        first_name = input('имя  ')
                        last_name = input('фамилия ')
                        email = input('e-amil ')
                        change_client(conn, id, first_name, last_name, email)
                    case '3':
                        del_phones(conn, id)
                    case '4':
                        df = input('Вы действительно хотите удалить данные об этом клиенте? Y/N \n')
                        if df == 'Y':
                            del_client(conn, id)
                        else:
                            if df == 'N':
                                print('Удаление отменено')
                            else:
                                print('Некорректный ввод, действие отменено')

            else:
                print('Клиент не найден')

        case '3':
            print('Введите данные, которые Вам известны:')
            first_name = input('имя ')
            if first_name == '':
                first_name = '%'
            last_name = input('фамилия ')
            if last_name == '':
                last_name = '%'

            email = input('e-mail ')
            if email == '':
                email = '%'

            phone = input('телефон')
            if phone == '':
                phone ='%'

            find_info_client(conn, first_name, last_name, email, phone)
conn.close()