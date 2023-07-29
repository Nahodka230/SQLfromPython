#from nis import match

import psycopg2
class Client:
    def __init__(self):
        self.first_name = input('Введите имя: ')
        self.last_name = input('Введите фамилию: ')
        self.email = input('Введите e-mail: ')
    def add_client(self,cur):

            cur.execute("""
            INSERT INTO client(first_name, last_name, email) VALUES (%s, %s, %s) RETURNING client_id;
            """, (self.first_name, self.last_name, self.email))
            id = cur.fetchone()[0]
            print('Клиент добавлен')
            return id

    def find_client(self, cur):

        if self.first_name == '':
            self.first_name = "%"

        if self.last_name == '':
            self.last_name = "%"

        if self.email == '':
            self.email = "%"

        cur.execute("""
                        SELECT * FROM client WHERE first_name LIKE %s AND last_name LIKE %s AND email LIKE %s;
                        """, (self.first_name, self.last_name, self.email))
        conn.commit()
        if cur.rowcount > 1:

            print('Найдены следующие записи: \n',)
            for item in cur.fetchall():
                print(f"ID: {item[0]}, Имя: {item[1]}, фамилия: {item[2]}, email: {item[3]} \n")
            id = input('Введите ID клиента, данные о котором нужно изменить:')
            return id
        else:
            if cur.rowcount == 1:
                #print(f'Найдена следующая запись: {cur.fetchone()}')
                id = cur.fetchone()[0]
                return id
            else:
                return 'None'
def create_db(cur):


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

def add_phones(cur, id):
    phones = input('Введите номер телефона клиента:')
    cur.execute("""
                        INSERT INTO phone_number(phones, client_id) VALUES (%s, %s) RETURNING phones, client_id;
                        """, (phones, id))
    conn.commit()
    print('Номер телефона добавлен.')

def change_client(cur, id, first_name, last_name, email):
    if first_name != '':

        cur.execute("""
                        UPDATE client SET first_name = %s WHERE client_id = %s;
                        """, (first_name, id))
        conn.commit()
    if last_name != '':
        cur.execute("""
                            UPDATE client SET last_name = %s WHERE client_id = %s;
                            """, (last_name, id))
        conn.commit()
    if email != '':
        cur.execute("""
                                UPDATE client SET email = %s WHERE client_id = %s;
                                """, (email, id))
        conn.commit()
    print('ДАННЫЕ О КЛИЕНТЕ ИЗМЕНЕНЫ \n')
    cur.execute("""
                                SELECT phones FROM phone_number WHERE client_id = %s;
                                """, (id,))
    conn.commit
    if cur.rowcount != 0:
        print( f'Для данного клиента найдены следующие номера телефонов:' ,cur.fetchall())
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

def del_phones(cur, id_client):

        cur.execute("""SELECT phones FROM phone_number WHERE client_id = %s;
                       """, (id_client,))
        print(f'Для данного клиента найдены следующие номера телефонов: ', cur.fetchall())
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
def del_client(cur, id):

        cur.execute("""DELETE FROM  phone_number WHERE client_id=%s;
                                """, (id,))
        cur.execute("""DELETE FROM  client WHERE client_id=%s;
                                        """, (id,))
        conn.commit()
        print('Данные о клиенте удалены')

def find_info_client(cur, first_name, last_name, email, phone):
        if phone!= '%':
            cur.execute(
                """SELECT * FROM client c LEFT JOIN phone_number p ON c.client_id=p.client_id WHERE c.first_name LIKE %s AND c.last_name LIKE %s AND c.email  LIKE %s AND (p.phones LIKE %s);""",
                (first_name, last_name, email, phone))
        else:
            cur.execute("""SELECT * FROM client c LEFT JOIN phone_number p ON c.client_id=p.client_id WHERE c.first_name LIKE %s AND c.last_name LIKE %s AND c.email  LIKE %s AND (p.phones LIKE %sOR p.phones IS NULL);""", (first_name,last_name,email,phone))
        for item in cur.fetchall():
            print(f"Имя: {item[1]}, фамилия: {item[2]}, email: {item[3]}, телефон: {item[5]} \n")

if __name__ == "__main__":

    with psycopg2.connect(database="client", user="postgres", password="") as conn:
        with conn.cursor() as cur:
            create_db(cur)

            f = input('Выберите действие: '
                  '\n 1 - Добавить нового клиента '
                  '\n 2 - Изменить/удалить данные о существующем клиенте (в том числе телефон)'
                  '\n 3 - Найти клиента \n')
            match f:
                case '1':
                    New_client = Client()
                    id = New_client.add_client(cur)
                    f = input ('Добавить телефон? Y/N \n')
                    while f == 'Y':
                        add_phones(conn, id)
                        f = input ('Добавить телефон? Y/N \n')

                case '2':
                    Edit_client = Client()
                    id = Edit_client.find_client(cur)
                    if id != 'None':
                        ef = input('Выберите действие:'
                          '\n1-добавить телефон'
                          '\n2-изменить данные о клиенте'
                          '\n3-удалить телефон'
                          '\n4-удалить клиента\n'
                          )
                        match ef:
                            case '1':
                                add_phones(cur, id)
                            case '2':
                                print('Введите новые данные клиента, которые необходимо заменить: \n')
                                first_name = input('имя  ')
                                last_name = input('фамилия ')
                                email = input('e-amil ')
                                change_client(cur, id, first_name, last_name, email)
                            case '3':
                                del_phones(cur, id)
                            case '4':
                                df = input('Вы действительно хотите удалить данные об этом клиенте? Y/N \n')
                                if df == 'Y':
                                    del_client(cur, id)
                                else:
                                    if df == 'N':
                                        print('Удаление отменено')
                                    else:
                                        print('Некорректный ввод, действие отменено')

                    else:
                        print('Клиент не найден')


    #вызов функции в теле программы

                case '3':
                    print('Введите данные, которые Вам известны:')
                    first_name = input('имя ')
                    if first_name == '':
                        first_name = "%"
                    last_name = input('фамилия ')
                    if last_name == '':
                        last_name = "%"

                    email = input('e-mail ')
                    if email == '':
                        email = "%"

                    phone = input('телефон')
                    if phone == '':
                        phone ="%"

                    find_info_client(cur, first_name, last_name, email, phone)
    conn.close()