#!/usr/bin/env python3

import sys

import requests
from settings import *


def submit(task_path: str, checker: str, rlz_file: str ='realization.sql'):

    user_file = f'{task_path}/{rlz_file}'

    try:
        with open(user_file, 'r', encoding="utf8") as u_file:
            user_code = u_file.read()
    except FileNotFoundError:
        print(f'{TerminalColors.WARNING}Не найден файл `{user_file}{TerminalColors.ENDC}`\n\nСохраните решение в {task_path}/{rlz_file}')
        sys.exit()

    try:
        r = requests.post(
            f'{CHECK_SERVICE_HOST}/{checker}',
            json={
                "student": student,
                "user_code": user_code
            },
            timeout=300
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        if 'result_key' in r.json()['response']['payload']:
            print(
                f"\n{TerminalColors.OKGREEN}{r.json()['response']['payload']['message']}{TerminalColors.ENDC}\n")
            print(
                f"Ключ: {TerminalColors.HEADER}{r.json()['response']['payload']['result_key']}{TerminalColors.ENDC}\n")
        else:
            print(
                f"\n{TerminalColors.FAIL}{r.json()['response']['payload']['message']}{TerminalColors.ENDC}\n")
    else:
        print(
            f'{TerminalColors.FAIL}Что-то пошло не так, сервер вернул ошибку {r.status_code}\n{checker}{TerminalColors.ENDC}')

