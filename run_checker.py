#!/usr/bin/env python3

import sys

import requests

from settings import CHECK_SERVICE_HOST, TerminalColors, pg_settings, student

API_PATH = 'api/v1/checks'


def submit(task_path: str, checker: str, rlz_file: str = 'realization.sql'):

    user_file = f'{task_path}/{rlz_file}'

    try:
        with open(user_file, 'r', encoding="utf8") as u_file:
            user_code = u_file.read()
    except FileNotFoundError:
        print(f'{TerminalColors.WARNING}Не найден файл `{user_file}{TerminalColors.ENDC}`\n\nСохраните решение в {task_path}/{rlz_file}')
        sys.exit()

    try:
        r = requests.post(
            f'http://{CHECK_SERVICE_HOST}/{API_PATH}/{checker}',
            json={
                "student_id": student,
                "student_solution": user_code,
                "student_db_connection": pg_settings
            },
            timeout=300
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        if r.json()['status'] == 'success':
            print(f'\n{TerminalColors.OKGREEN}{r.json()["message"]}{TerminalColors.ENDC}\n')
        else:
            print(f'\n{TerminalColors.FAIL}{r.json()["message"]}{TerminalColors.ENDC}\n')
    else:
        print(
            f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}\n{checker}{TerminalColors.ENDC}')


def healthcheck():
    checker = 'api/v1/health/healthcheck'
    try:
        r = requests.get(
            f'http://{CHECK_SERVICE_HOST}/{checker}'
        )

    except Exception as e:
        return e
    return r, r.content


def init():
    checker = 'api/v1/dbschema/init'
    try:
        r = requests.post(
            f'http://{CHECK_SERVICE_HOST}/{checker}',
            json={
                'student_id': student,
                'lesson_key': 'de01010101',
                'student_db_connection': pg_settings
            }
        )

    except Exception as e:
        return e
    return r, r.content


if __name__ == '__main__':
    print(f'{healthcheck() = }')
    print(f'{init() = }')
