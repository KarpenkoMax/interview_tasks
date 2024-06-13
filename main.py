import os
import sqlite3
from datetime import datetime

"""
ПОЯСНЕНИЯ

данные в базе в процессе отладки изменились, но при желании можно заменить файл в папке db

assumptions
1. Все операции по фильтрации, агрегации и т.п., кроме подстановки даты, должны быть сделано при помощи SQL
2. Рассылки по регистрации и по активности - 2 разные сущности, так что одному пользователю может быть отправлено что-то одно, или оба сообщения сразу.
Это, в свою очередь, усложняет учет отправленных сообщений
3. В один и тот же день письма по активности одному и тому же пользователю не отправлялись - в противном случае записи в результате будут дублироваться,
   что, при уже достаточной сложности скрипта, проще отлавливать уже в программе
4. По алгоритму для в.2 - сообщение отправится, если прошло нужное кол-во дней и с последней активности по введенную дату:
    - либо не было сообщений по активности
    - либо были сообщения о меньшем кол-ве дней

"""

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
    ondate = datetime(2024, 6, 15)
    print(f'For date {ondate.strftime('%Y-%m-%d')}:')

    template = "{0:8}|{1:20}|{2:35}|{3:35}"

    # вариант 1 (если отправлялись сообщения - больше не шлём)
    res_list = fetch_user_message_list(ondate, on_existing_sent='skip')

    # в целях тестирования/оценки скрипт возвращает больше данных, чем необходимо, поэтому тут они обрезаются
    print_list = [(x[0], x[1], x[8], x[9]) for x in res_list]

    print('Список по в.1')
    print(template.format('user_id', 'username', 'reg_message', 'activity_message'))
    for rec in print_list:
        print(template.format(rec[0], rec[1], rec[2] if rec[2] is not None else '-', rec[3] if rec[3] is not None else '-'))

    # вариант 2 (если отправлялись сообщения - отправлять, если прошел срок)
    res_list = fetch_user_message_list(ondate, on_existing_sent='recalc')

    print_list = [(x[0], x[1], x[8], x[9]) for x in res_list]

    print('Список по в.2')
    print(template.format('user_id', 'username', 'reg_message', 'activity_message'))
    for rec in print_list:
        print(template.format(rec[0], rec[1], rec[2] if rec[2] is not None else '-', rec[3] if rec[3] is not None else '-'))