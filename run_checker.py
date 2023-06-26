import os
import sys
import json

import requests

from settings import STUDENT

INVITE_TOKEN = "5aa046d73fd004ea6e6f527b8cd0ef08fd13e12877377407565c244dc630a872"  # noqa

TOKEN_PATH = ".check_service_token"
PUBLIC_CHECK_SERVICE_HOST = "https://de-sprint1-checks.sprint9.tgcloudenv.ru"
CHECK_SERVICE_HOST = os.getenv("CHECK_SERVICE_HOST", PUBLIC_CHECK_SERVICE_HOST)
API_PATH = "api/v1/checks"


class TokenRepository:
    def __init__(self, token_path):
        self.token_path = token_path

    def get_token(self):
        try:
            with open(self.token_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def save_token(self, token):
        with open(self.token_path, "w") as f:
            f.write(token)


token_repository = TokenRepository(TOKEN_PATH)


def service_error(status_code, address):
    print('Что-то пошло не так, сервер вернул ошибку '
          f'{status_code}\n{address}\nПовторите запрос через минуту.')


def auth_user():
    address = "api/v1/auth/token/"

    try:
        r = requests.post(
            f"{CHECK_SERVICE_HOST}/{address}",
            data={"username": str(STUDENT), "password": str(INVITE_TOKEN)},
        )

    except Exception as e:
        print("Не получилось создать пользователя из-за ошибки.")
        print(e)
        return

    if r.status_code == 200:
        token_repository.save_token(r.json()["access_token"])
    elif r.status_code == 400:
        print("Не получилось создать пользователя")
    else:
        service_error(r.status_code, address)


def headers():
    return {"Authorization": f"Bearer {token_repository.get_token()}"}


def create_playground():
    auth_user()

    address = "api/v1/playgrounds/"
    try:
        r = requests.post(
            f"{CHECK_SERVICE_HOST}/{address}",
            headers=headers(),
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        response = r.json()
        message = response.pop('message', None)
        response.pop('student_id', None)
        response.pop('secret_key', None)
        print('Параметры подключения:\n'
              f'{json.dumps(response, indent=1)}\n'
              f'{message}')

    elif r.status_code == 400:
        print(f"{r.json()['message']}")
    else:
        service_error(r.status_code, address)


def get_playground():
    address = "api/v1/playgrounds/"
    try:
        r = requests.get(
            f"{CHECK_SERVICE_HOST}/{address}",
            headers=headers(),
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        response = r.json()
        response.pop('message', None)
        response.pop('student_id', None)
        response.pop('secret_key', None)
        print('\nПараметры подключения:\n'
              f"{json.dumps(response['student_db_connection'], indent=1)}")
    elif r.status_code == 400:
        print(f"Что-то пошло не так, сервер вернул ошибку {r.status_code}")
    elif r.status_code == 401:
        message_401()
    elif r.status_code == 504:
        print(f"Пользователь с логином `{STUDENT}` не найден, сперва запусти"
              "те `Тема 2. Инструменты/2.4 Запустите среду для"
              " тестирования/submit.py`")
    else:
        service_error(r.status_code, address)


def message_401():
    print('Не авторизованный доступ, выполните запуск `Тема 2. '
          'Инструменты/2.4 Запустите среду для тестирования/submit.py')


def submit(task_path: str, checker: str, rlz_file: str = "realization.sql"):
    user_file = f"{task_path}/{rlz_file}"

    try:
        with open(user_file, "r", encoding="utf8") as u_file:
            user_code = u_file.read()
    except FileNotFoundError:
        print(f'Не найден файл `{user_file}\n'
              f'Сохраните решение в {task_path}/{rlz_file}')
        sys.exit()

    try:
        r = requests.post(
            f"{CHECK_SERVICE_HOST}/{API_PATH}/{checker}/",
            json={"student_id": STUDENT, "student_solution": user_code},
            headers=headers(),
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        if r.json()["status"] == "success":
            print(f'\n{r.json()["message"]}\n')
        else:
            print(f'\n{r.json()["message"]}\n')
    elif r.status_code == 401:
        message_401()
    else:
        service_error(r.status_code, checker)


def healthcheck():
    checker = "api/v1/health/healthcheck"
    try:
        r = requests.get(f"{CHECK_SERVICE_HOST}/{checker}")

    except Exception as e:
        return e
    return r, r.content


if __name__ == "__main__":
    print(f"{healthcheck() = }")
