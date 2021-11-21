import os
import requests

from collections import defaultdict
from itertools import count
from terminaltables import AsciiTable

MOSCOW_AREA = 1


def get_hh_vacancies_response(request, page=0):
    params = {
        "text": request,
        "area": MOSCOW_AREA,
        "period": 30,
        "currency": "RUR",
        "per_page": 50,
        "page": page
    }
    result = requests.get("https://api.hh.ru/vacancies", params=params)
    result.raise_for_status()
    return result.json()


def fetch_hh_vacancies(request: str):
    result = []
    first_request = get_hh_vacancies_response(request)
    pages = first_request["pages"]
    result.extend(first_request["items"])
    for page in range(pages):
        result.extend(get_hh_vacancies_response(request, page=page)["items"])
    return result


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
    params = {
        "keyword": request,
        "town": "Москва",
        "period": 30,
        "count": 50,
        "page": page
    }
    result = requests.get(
        url="https://api.superjob.ru/2.0/vacancies",
        headers={"X-Api-App-Id": sj_token},
        params=params
    )
    result.raise_for_status()
    return result.json()


def fetch_sj_vacancies(sj_token):
    result = []

    def wrapper(request):
        for page in count():
            data = get_sj_vacancies_response(request, page=page, sj_token=sj_token)
            result.extend(data['objects'])
            if not data["more"]:
                break

    return wrapper


def get_languages_vacancies(fetch_function, languages):
    vacancies = defaultdict(list)
    for language in languages:
        vacancies[language].extend(fetch_function(language))
    return vacancies


def prepare_stat_table(title, vacancies, predict_func):
    table_data = [
        ("Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата")
    ]

    languages = vacancies.keys()

    for language in languages:
        vacancies_amount = len(vacancies["language"])
        not_zero_salaries = [predict_func(vac) for vac in vacancies["language"] if predict_func(vac)]
        vacancies_with_salary = len(not_zero_salaries)

        if vacancies_with_salary:
            table_data.append(
                (
                    language,
                    vacancies_amount,
                    vacancies_with_salary,
                    int(sum(not_zero_salaries)) / vacancies_with_salary,
                )
            )

    table = AsciiTable(table_data, title)
    table.justify_columns[2] = 'left'
    return table


def main():
    SJ_TOKEN = os.getenv("SJ_TOKEN")
    languages = ["Python", "Java", "JavaScript"]

    hh_language_vacancies = get_languages_vacancies(fetch_hh_vacancies, languages)
    sj_language_vacancies = get_languages_vacancies(fetch_sj_vacancies(sj_token=SJ_TOKEN), languages)

    hh_table = prepare_stat_table("HH Moscow", hh_language_vacancies, predict_hh_salary)
    sj_table = prepare_stat_table("SuperJob Moscow", sj_language_vacancies, predict_sj_salary)

    print(hh_table.table)
    print(sj_table.table)


if __name__ == '__main__':
    main()
