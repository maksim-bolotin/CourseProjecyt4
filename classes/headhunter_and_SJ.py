import requests
import json
from os import getenv
from classes.abstract_parser_classes import VacancyAPI, VacancyManager


class Vacancy:
    """
    Класс для работы с вакансиями.
    """
    def __init__(self, title, link, salary, description):
        self.title = title
        self.link = link
        self.salary = salary
        self.description = description

    def comparison_by_salary(self, other):
        # метод для сравнения вакансий по зарплатам.
        self_salary_min, self_salary_max = map(int, self.salary.split('-'))
        other_salary_min, other_salary_max = map(int, other.salary.split('-'))
        self_avg_salary = (self_salary_min + self_salary_max) / 2
        other_avg_salary = (other_salary_min + other_salary_max) / 2
        result = f"""{self.title} с зарплатой {self_avg_salary:.2f}
{'меньше' if self_avg_salary < other_avg_salary else 'больше'} чем {other.title} с зарплатой {other_avg_salary:.2f}"""
        return result

    def __repr__(self):
        return f"Vacancy('{self.title}', '{self.link}', '{self.salary}', '{self.description}')"

    def to_dict(self):
        # метод преобразования данных в словарь.
        return {
            "title": self.title,
            "link": self.link,
            "salary": self.salary,
            "description": self.description}


class HhVacancyAPI(VacancyAPI):
    """
    Класс для подключения к https://api.hh.ru/ и получения вакансий.
    """
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.hh.ru/"

    def get_vacancies(self, search_query):
        # метод для реализации получения вакансий с hh.ru
        url = f"{self.base_url}vacancies"
        params = {'text': search_query}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            vacancies = []
            for item in data['items']:
                title = item.get('name', '')
                link = item.get('alternate_url', '')
                salary = item['salary']['from'] if (item['salary']
                                                    and 'from' in item['salary']) else "Зарплата не указана"
                description = item['snippet']['responsibility'] if 'snippet' in item else ''
                new_vacancy = Vacancy(title, link, salary, description)
                vacancies.append(new_vacancy)
            return vacancies
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None


class JsonVacancyManager(VacancyManager):
    """
    Класс для работы с JSON файлом.
    """
    def __init__(self, file_path='vacancies.json'):
        self.file_path = file_path
        self.vacancies = []
        self.load_from_file()

    def load_from_file(self):
        # метод загрузки вакансий из файла.
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                if data:
                    self.vacancies = json.loads(data)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Ошибка при загрузке данных из файла: {e}")

    def save_data(self):
        # метод сохранения данных.
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.vacancies, file, ensure_ascii=False, indent=2)

    def add_vacancy(self, vacancy_data, search_keyword=None):
        # метод добавления вакансий в файл.
        if isinstance(vacancy_data, Vacancy):
            vacancy_data = vacancy_data.to_dict()
        # Проверка, существует ли уже вакансия с такой же ссылкой
        if not any(v.get("link") == vacancy_data.get("link") for v in self.vacancies):
            # Проверяем, есть ли ключевое слово в описании
            if search_keyword and search_keyword not in vacancy_data['description']:
                vacancy_data['description'] += f" {search_keyword}"
            self.vacancies.append(vacancy_data)
            self.save_data()
        else:
            print(f"Вакансия с ссылкой {vacancy_data['link']} уже существует в списке.")

    def get_vacancies(self, criteria):
        # реализация получения вакансий по заданному диапазону зарплаты.
        salary_range = criteria.get("salary")
        description_keyword = criteria.get("description")
        if salary_range:
            min_salary, max_salary = map(int, salary_range.split('-'))
            filtered_vacancies = [Vacancy(**v) for v in self.vacancies
                                  if v.get('salary') and min_salary <= v['salary'] <= max_salary]
        else:
            filtered_vacancies = [Vacancy(**v) for v in self.vacancies]

        # Дополнительная фильтрация по ключевому слову в описании
        if description_keyword:
            filtered_vacancies = [v for v in filtered_vacancies if description_keyword.lower() in v.description.lower()]
        return filtered_vacancies

    def delete_vacancy(self, index):
        # Метод удаления вакансии из файла по индексу.
        try:
            index = int(index)
            if 0 <= index < len(self.vacancies):
                del_vacancy = self.vacancies.pop(index)
                self.save_data()
                return del_vacancy
            else:
                return None
        except (ValueError, TypeError):
            return None


class SJVacancyAPI(VacancyAPI):
    """
    Класс для подключения к https://api.superjob.ru/2.0/ и получения вакансий.
    """
    sj_api_key = getenv('SJ_API_KEY')

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.superjob.ru/2.0/"

    def get_vacancies(self, search_query):
        # реализация получения вакансий с hh.ru
        url = f"{self.base_url}vacancies"
        params = {'text': search_query.encode('utf-8')}
        headers = {
            'X-Api-App-Id': self.sj_api_key,
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            vacancies = []
            for item in data['objects']:
                title = item.get('profession', '')
                link = item.get('link', '')
                salary = item.get('payment_to', '') if 'payment_to' in item else "Зарплата не указана"
                description = item['candidat'] if 'candidat' in item else ''
                new_vacancy = Vacancy(title, link, salary, description)
                vacancies.append(new_vacancy)
            return vacancies
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
