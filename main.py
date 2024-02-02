from classes.headhunter_and_SJ import HhVacancyAPI, JsonVacancyManager, Vacancy, SJVacancyAPI
from utils import print_vacancies


def user_interaction():
    hh_api = HhVacancyAPI()
    json_saver = JsonVacancyManager()
    vacancies = []
    superjob_api = SJVacancyAPI()

    while True:
        print("\n1. Выбрать источник вакансий")
        print("2. Добавить вакансию в файл")
        print("3. Получить вакансии из файла по критериям")
        print("4. Удалить вакансию из файла")
        print("5. Выйти")

        choice = input("Выберите действие: ")
        if choice == "1":
            print("\n1. HeadHunter")
            print("2. SuperJob")
            source_choice = input("Выберите источник вакансий: ")
            if source_choice == "1":
                vacancies = hh_api.get_vacancies(input("Введите поисковый запрос: "))
                print_vacancies(vacancies)
            elif source_choice == "2":
                vacancies = superjob_api.get_vacancies(input("Введите поисковый запрос: "))
                print_vacancies(vacancies)
            else:
                print("Неправильный выбор источника. Пожалуйста, выберите снова.")
        elif choice == "2":
            if vacancies:
                selected_index = int(input("Введите номер вакансии для добавления: ")) - 1
                try:
                    selected_vacancy_data = vacancies[selected_index]
                    selected_vacancy = Vacancy(selected_vacancy_data.title, selected_vacancy_data.link,
                                               selected_vacancy_data.salary, selected_vacancy_data.description)
                    json_saver.add_vacancy(selected_vacancy)
                    print("Вакансия успешно добавлена.")
                except IndexError:
                    print("несуществующая вакансия")
            else:
                print("нет вакансии для добавления")
        elif choice == "3":
            criteria = {"salary": input("Введите зарплату: "),
                        "description": input("Введите ключевое слово в описании: ")}
            matching_vacancies = json_saver.get_vacancies(criteria)
            print_vacancies(matching_vacancies)
        elif choice == "4":
            selected_index_to_remove = int(input("Введите номер вакансии для удаления: ")) - 1
            selected_vacancy_data_to_remove = vacancies[selected_index_to_remove]
            selected_vacancy_to_remove = Vacancy(selected_vacancy_data_to_remove["title"],
                                                 selected_vacancy_data_to_remove["link"],
                                                 selected_vacancy_data_to_remove["salary"],
                                                 selected_vacancy_data_to_remove["description"])
            json_saver.delete_vacancy(selected_vacancy_to_remove)
            print("Вакансия успешно удалена.")
        elif choice == "5":
            break
        else:
            print("Некорректный выбор. Пожалуйста, выберите снова.")


if __name__ == "__main__":
    user_interaction()
