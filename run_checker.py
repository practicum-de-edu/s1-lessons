#!/usr/bin/env python3

import sys

import requests

from settings import STUDENT

CHECK_SERVICE_HOST = 'https://de-sprint1-checks.sprint9.tgcloudenv.ru'
API_PATH = 'api/v1/checks'


class TerminalColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def create_playground():
    address = 'api/v1/playgrounds'
    try:
        r = requests.post(
            f'{CHECK_SERVICE_HOST}/{address}',
            json={
                'student_id': STUDENT
            }
        )

    except Exception as e:
        return print(e)

    if r.status_code == 200:
        print(f'\n{TerminalColors.OKGREEN}{r.json()}{TerminalColors.ENDC}\n')
    else:
        print(f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}\n{address}{TerminalColors.ENDC}')


def submit(task_path: str, checker: str, rlz_file: str = 'realization.sql'):

    user_file = f'{task_path}/{rlz_file}'

    try:
        with open(user_file, 'r', encoding="utf8") as u_file:
            user_code = u_file.read()
    except FileNotFoundError:
        print(f'{TerminalColors.WARNING}Не найден файл `{user_file}{TerminalColors.ENDC}`\n\nСохраните решение в {task_path}/{rlz_file}')  # noqa
        sys.exit()

    try:
        r = requests.post(
            f'{CHECK_SERVICE_HOST}/{API_PATH}/{checker}',
            json={
                "student_id": STUDENT,
                "student_solution": user_code
            },
            timeout=300
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        if r.json()['status'] == 'success':
            print(
                f'\n{TerminalColors.OKGREEN}{r.json()["message"]}{TerminalColors.ENDC}\n')
        else:
            print(
                f'\n{TerminalColors.FAIL}{r.json()["message"]}{TerminalColors.ENDC}\n')
    else:
        print(
            f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}\n{checker}{TerminalColors.ENDC}')


def healthcheck():
    checker = 'api/v1/health/healthcheck'
    try:
        r = requests.get(
            f'{CHECK_SERVICE_HOST}/{checker}'
        )

    except Exception as e:
        return e
    return r, r.content


if __name__ == '__main__':
    print(f'{healthcheck() = }')
