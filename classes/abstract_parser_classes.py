from abc import abstractmethod, ABC


class VacancyAPI(ABC):

    @abstractmethod
    def get_vacancies(self, search_query):
        pass


class VacancyManager(ABC):
    @abstractmethod
    def add_vacancy(self, vacancy):
        pass

    @abstractmethod
    def get_vacancies(self, criteria):
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy):
        pass
