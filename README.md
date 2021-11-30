# Сравниваем вакансии программистов

Проект анализирует данные по вакансиям на [hh.ru](https://hh.ru) и [superjob.ru](https://superjob.ru) и выдаёт результаты в формате таблиц.

### Как установить

Для того чтобы получить данные с superjob нужно получить [API токен](https://api.superjob.ru/#access_token).

Установка зависимостей проекта выполняется стандартно:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Как запустить проект:

Чтобы запустить проект, нужно выставить [переменную окржения](https://ru.hexlet.io/courses/cli-basics/lessons/environment-variables/theory_unit) с названием SJ_TOKEN и равной вашему токену от superjob:

```sh
export SJ_TOKEN=...
```

после чего выполнить запуск программы:

```sh
python main.py
```

Проект разработан и протестирован для версии Python 3.8.

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).