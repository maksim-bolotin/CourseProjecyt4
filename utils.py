def print_vacancies(vacancies):
    print("Список вакансий:")
    for i, vacancy in enumerate(vacancies, start=1):
        print(f"{i}. {vacancy.title}")
        print(f"   Ссылка: {vacancy.link}")
        print(f"   Зарплата: {vacancy.salary}")
        print(f"   Требования: {vacancy.description}")
        print("\n")
