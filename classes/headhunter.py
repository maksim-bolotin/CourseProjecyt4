import requests
import json
from classes.abstract_parser_classes import VacancyAPI, VacancyManager


class Vacancy:
    def __init__(self, title, link, salary, description):
        self.title = title
        self.link = link
        self.salary = salary
        self.description = description

    def comparison_by_salary(self, other):
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
        return {
            "title": self.title,
            "link": self.link,
            "salary": self.salary,
            "description": self.description}


class HhVacancyAPI(VacancyAPI):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.hh.ru/"

    def get_vacancies(self, search_query):
        # реализация получения вакансий с hh.ru
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
                salary = item['salary']['from'] if item['salary'] and 'from' in item['salary'] else None
                description = item['snippet']['responsibility'] if 'snippet' in item else ''
                new_vacancy = Vacancy(title, link, salary, description)
                vacancies.append(new_vacancy)
            return vacancies
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None


class JsonVacancyManager(VacancyManager):
    def __init__(self, file_path='vacancies.json'):
        self.file_path = file_path
        self.vacancies = []
        self.load_from_file()

    def load_from_file(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                if data:
                    self.vacancies = json.loads(data)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Ошибка при загрузке данных из файла: {e}")

    def save_data(self):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.vacancies, file, ensure_ascii=False)

    def add_vacancy(self, vacancy_data):
        # Преобразование объекта Vacancy в словарь, если он имеет атрибуты
        if isinstance(vacancy_data, Vacancy):
            vacancy_data = vacancy_data.to_dict()

        # Проверка, существует ли уже вакансия с такой же ссылкой
        if not any(v.get("link") == vacancy_data.get("link") for v in self.vacancies):
            self.vacancies.append(vacancy_data)
            self.save_data()
        else:
            print(f"Вакансия с ссылкой {vacancy_data['link']} уже существует в списке.")

    def get_vacancies(self, salary_range):
        # Реализация получения вакансий по заданному диапазону зарплаты.
        filtered_vacancies = [Vacancy(**v) for v in self.vacancies if salary_range in v['salary']]
        return sorted(filtered_vacancies, key=lambda x: x.salary)

    def delete_vacancy(self, vacancy):
        self.vacancies = [v for v in self.vacancies if v != vars(vacancy)]
        self.save_data()
