#!/usr/bin/env python3

import os
import sys

import requests

from settings import INVITE_TOKEN, STUDENT

TOKEN_PATH = '.check_service_token'
PUBLIC_CHECK_SERVICE_HOST = 'https://de-sprint1-checks.sprint9.tgcloudenv.ru'
CHECK_SERVICE_HOST = os.getenv('CHECK_SERVICE_HOST', PUBLIC_CHECK_SERVICE_HOST)
API_PATH = 'api/v1/checks'


class TokenRepository:
    def __init__(self, token_path):
        self.token_path = token_path

    def get_token(self):
        try:
            with open(self.token_path, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def save_token(self, token):
        with open(self.token_path, 'w') as f:
            f.write(token)


token_repository = TokenRepository(TOKEN_PATH)


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


def auth_user():
    address = 'api/v1/auth/token/'

    try:
        r = requests.post(
            f'{CHECK_SERVICE_HOST}/{address}',
            data={
                'username': str(STUDENT),
                "password": str(INVITE_TOKEN)
            }
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        token_repository.save_token(r.json()['access_token'])
        print(f'\n{TerminalColors.OKGREEN}{r.json()}{TerminalColors.ENDC}\n')
    elif r.status_code == 400:
        print(f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}{TerminalColors.ENDC}')
        print(f'\n{TerminalColors.WARNING}{r.json()}{TerminalColors.ENDC}\n')
    else:
        print(f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}\n{address}{TerminalColors.ENDC}')
        print(r.json())


def create_playground():
    address = 'api/v1/playgrounds/'
    try:
        r = requests.post(
            f'{CHECK_SERVICE_HOST}/{address}',
            headers={"Authorization": f"Bearer {token_repository.get_token()}"}
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        print(f'\n{TerminalColors.OKGREEN}{r.json()}{TerminalColors.ENDC}\n')
    elif r.status_code == 400:
        print(f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}{TerminalColors.ENDC}')
        print(f'\n{TerminalColors.WARNING}{r.json()}{TerminalColors.ENDC}\n')
    else:
        print(f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}\n{address}{TerminalColors.ENDC}')
        print(r.json())


def get_playground():
    address = 'api/v1/playgrounds/'
    try:
        r = requests.get(
            f'{CHECK_SERVICE_HOST}/{address}',
            headers={"Authorization": f"Bearer {token_repository.get_token()}"},
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        print(f'\n{TerminalColors.OKGREEN}{r.json()}{TerminalColors.ENDC}\n')
    elif r.status_code == 400:
        print(f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}{TerminalColors.ENDC}')
        print(f'\n{TerminalColors.WARNING}{r.json()}{TerminalColors.ENDC}\n')
    else:
        print(f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}\n{address}{TerminalColors.ENDC}')
        print(r.json())


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
            f'{CHECK_SERVICE_HOST}/{API_PATH}/{checker}/',
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
            print(f'\n{TerminalColors.OKGREEN}{r.json()["message"]}{TerminalColors.ENDC}\n')
        else:
            print(f'\n{TerminalColors.FAIL}{r.json()["message"]}{TerminalColors.ENDC}\n')
    else:
        print(f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}\n{checker}{TerminalColors.ENDC}')
        print(r.json())


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
