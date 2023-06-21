#from nis import match

import psycopg2
import pprint
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

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO client(first_name, last_name, email) VALUES (%s, %s, %s) RETURNING client_id;
        """, (first_name, last_name, email))
        id = cur.fetchone()[0]
        conn.commit()
        if phones:

            cur.execute("""
                    INSERT INTO phone_number(phones, client_id) VALUES (%s, %s) RETURNING phones, client_id;
                    """,(phones, id))
            conn.commit()

def find_client(conn, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT client_id FROM client WHERE first_name = %s AND last_name = %s AND email = %s;
                    """, (first_name,last_name, email))
        if cur.rowcount !=0:
            return cur.fetchone()[0]
        else:
            return 'None'
def add_phones(conn, id, phones):
    with conn.cursor() as cur:
        cur.execute("""
                        INSERT INTO phone_number(phones, client_id) VALUES (%s, %s) RETURNING phones, client_id;
                        """, (phones, id))
        print(cur.fetchone())
    conn.commit()
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

with psycopg2.connect(database="client", user="postgres", password="230105") as conn:
    create_db(conn)
    f = input('Выберите действие: '
              '\n 1 - Добавить нового клиента '
              '\n 2 - Добавить телефон для существующего клиента '
              '\n 3 - Изменить данные о клиенте '
              '\n 4 - удалить телефон для существующего клиента'
              '\n 5 - удалить существующего клиента\n')
    match f:
        case '1':
            first_name = input('Введите имя: ')
            last_name = input('Введите фамилию: ')
            email = input('Введите e-amil: ')
            phones = input('Введите номер телефона:')
            add_client(conn, first_name, last_name, email, phones)
        case '2':
            first_name = input('Введите имя: ')
            last_name = input('Введите фамилию: ')
            email = input('Введите e-mail: ')
            id = find_client(conn, first_name, last_name, email)
            if id != 'None':
                phones = input('Введите добавляемый номер телефона:')
                add_phones(conn,id,phones)
            else:
                print('Клиент не найден')
        case '3':
            first_name = input('Введите имя клиента, данные о котором хотите изменить: ')
            last_name = input('Введите фамилию клиента, данные о котором хотите изменить: ')
            email = input('Введите e-mail клиента, данные о котором хотите изменить: ')
            id = find_client(conn, first_name, last_name, email)
            if id != 'None':
                print('Введите новые данные клиента: \n')
                first_name = input('имя  ')
                last_name = input('фамилия ')
                email = input('e-amil ')

                change_client(conn, id, first_name, last_name, email)

            else:
                print('Клиент не найден')
        case '4':
            first_name = input('Введите имя: ')
            last_name = input('Введите фамилию: ')
            email = input('Введите e-mail: ')
            id = find_client(conn, first_name, last_name, email)
            if id != 'None':
                del_phones(conn,id)
            else:
                print('Клиент не найден')
        case '5':
            first_name = input('Введите имя: ')
            last_name = input('Введите фамилию: ')
            email = input('Введите e-mail: ')
            id = find_client(conn, first_name, last_name, email)
            if id != 'None':
                del_client(conn, id)
            else:
                print('Клиент не найден')

conn.close()