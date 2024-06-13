import os
import sqlite3
from datetime import datetime

DB_FILENAME = 'db_test_zadanie.sqlite'
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_SCRIPT_DIR = os.path.join(APP_DIR, 'sql_scripts')
DB_DIR = os.path.join(APP_DIR, 'db')

SQL_SCRIPT_1_FILENAME = '1.sql'
SQL_SCRIPT_2_FILENAME = '2.sql'



def fetch_user_message_list(date: datetime, on_existing_sent: str = 'skip') -> list:
    """
    Получает по дате при помощи sql скрипта список с подходящими сообщениями для пользователей

    :date: datetime - дата, по разнице с которой определяются сообщения
    :on_existing_sent: str 'skip' | 'recalc' - режим учёта уже отправленных сообщений (skip - не отправлять, recalc - просчитать по дате)
    """
    res_list = []

    with sqlite3.connect(os.path.join(DB_DIR, DB_FILENAME)) as conn:
        
        try:
            cursor = conn.cursor()

            if on_existing_sent == 'skip':
                query = open(os.path.join(SQL_SCRIPT_DIR, SQL_SCRIPT_1_FILENAME), 'r', encoding='UTF-8')
            elif on_existing_sent == 'recalc':
                query = open(os.path.join(SQL_SCRIPT_DIR, SQL_SCRIPT_2_FILENAME), 'r', encoding='UTF-8')
            else:
                raise ValueError('on_existing_sent parameter has inapropriate value')

            sql_as_string = query.read().format(date.strftime('%Y-%m-%d'))
            res = cursor.execute(sql_as_string)
            res_list = res.fetchall()

        except Exception as e:
            print('smth went wrong')
            raise(e)

        print('')
        
    return res_list

if __name__ == '__main__':
    ondate = datetime(2024, 5, 15)
    print(f'For date {ondate.strftime('%Y-%m-%d')}:')

    # вариант 1 (если отправлялись сообщения - больше не шлём)
    res_list = fetch_user_message_list(ondate, on_existing_sent='skip')

    print_list = res_list#[(x[0], x[1], x[9], x[10]) for x in res_list]

    print('Список по в.1')

    for rec in print_list:
        print(rec)

    # вариант 2 (если отправлялись сообщения - отправлять, если прошел срок)
    res_list = fetch_user_message_list(ondate, on_existing_sent='recalc')

    print_list = res_list#[(x[0], x[1], x[9], x[10]) for x in res_list]

    print('Список по в.2')

    for rec in print_list:
        print(rec)