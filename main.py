import os
import requests

from collections import defaultdict
from itertools import count
from terminaltables import AsciiTable


def get_hh_vacancies_response(request, page=0, area=1):
    vacancies_response = requests.get(
        url="https://api.hh.ru/vacancies",
        params={
            "text": request,
            "area": area,
            "period": 30,
            "currency": "RUR",
            "per_page": 50,
            "page": page
        })
    vacancies_response.raise_for_status()
    return vacancies_response.json()


def fetch_hh_vacancies(request: str):
    vacancies = []
    first_request = get_hh_vacancies_response(request)
    pages = first_request["pages"]
    vacancies.extend(first_request["items"])
    for page in range(pages):
        vacancies.extend(get_hh_vacancies_response(request, page=page)["items"])
    return vacancies


def predict_salary(_from, to):
    if not _from and not to:
        return 0
    if _from and to:
        return int((_from + to) / 2)
    elif _from:
        return int(_from * 1.2)

    return int(to * 0.8)


def predict_hh_salary(vacancy):
    salary_from = vacancy["salary"]["from"]
    salary_to = vacancy["salary"]["to"]
    return predict_salary(salary_from, salary_to)


def predict_sj_salary(vacancy):
    salary_from = vacancy["payment_from"]
    salary_to = vacancy["payment_to"]
    return predict_salary(salary_from, salary_to)


def get_sj_vacancies_response(request, sj_token, page=0):
    vacancies_response = requests.get(
        url="https://api.superjob.ru/2.0/vacancies",
        headers={"X-Api-App-Id": sj_token},
        params={
            "keyword": request,
            "town": "Москва",
            "period": 30,
            "count": 50,
            "page": page
        }
    )
    vacancies_response.raise_for_status()
    return vacancies_response.json()


def fetch_sj_vacancies(sj_token):
    vacancies = []

    def wrapper(request):
        for page in count():
            data = get_sj_vacancies_response(request, page=page, sj_token=sj_token)
            vacancies.extend(data['objects'])
            if not data["more"]:
                break

    return wrapper


def get_language_vacancies(fetch_function, languages):
    vacancies = defaultdict(list)
    for language in languages:
        vacancies[language].extend(fetch_function(language))
    return vacancies


def prepare_stat_table(title, vacancies, predict_func):
    vacancies_table_data = [
        ("Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата")
    ]

    languages = vacancies.keys()

    for language in languages:
        vacancies_amount = len(vacancies["language"])
        not_zero_salaries = [
            predict_func(vacancy) for vacancy in vacancies["language"] if predict_func(vacancy)
        ]
        vacancies_with_salary = len(not_zero_salaries)

        if vacancies_with_salary:
            vacancies_table_data.append(
                (
                    language,
                    vacancies_amount,
                    vacancies_with_salary,
                    int(sum(not_zero_salaries)) / vacancies_with_salary,
                )
            )

    vacancies_table = AsciiTable(vacancies_table_data, title)
    vacancies_table.justify_columns[2] = 'left'
    return vacancies_table


def main():
    languages = ["Python", "Java", "JavaScript"]

    hh_language_vacancies = get_language_vacancies(fetch_hh_vacancies, languages)
    sj_language_vacancies = get_language_vacancies(fetch_sj_vacancies(sj_token=os.getenv("SJ_TOKEN")), languages)

    hh_table = prepare_stat_table("HH Moscow", hh_language_vacancies, predict_hh_salary)
    sj_table = prepare_stat_table("SuperJob Moscow", sj_language_vacancies, predict_sj_salary)

    print(hh_table.table)
    print(sj_table.table)


if __name__ == '__main__':
    main()
