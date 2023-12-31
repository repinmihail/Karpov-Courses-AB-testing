import numpy as np
import pandas as pd

class SequentialTester:
    def __init__(
        self, metric_name, time_column_name,
        alpha, beta, pdf_one, pdf_two
    ):
        """Создаём класс для проверки гипотезы о равенстве средних тестом Вальда.

        Предполагается, что среднее значение метрики у распределения альтернативной
        гипотезы с плотность pdf_two больше.

        :param metric_name: str, название стобца со значениями измерений.
        :param time_column_name: str, названия столбца с датой и временем измерения.
        :param alpha: float, допустимая ошибка первого рода.
        :param beta: float, допустимая ошибка второго рода.
        :param pdf_one: function, функция плотности распределения метрики при H0.
        :param pdf_two: function, функция плотности распределения метрики при H1.
        """
        self.metric_name = metric_name
        self.time_column_name = time_column_name
        self.alpha = alpha
        self.beta = beta
        self.pdf_one = pdf_one
        self.pdf_two = pdf_two
        # YOUR_CODE_HERE
        self.lower_bound = np.log(self.beta / (1 - self.alpha))
        self.upper_bound = np.log((1 - self.beta) / self.alpha)

        self.data_control_history = None
        self.data_pilot_history = None
        

    def run_test(self, data_control, data_pilot):
        """
        Запускаем новый тест, проверяет гипотезу о равенстве средних.
        
        :param data_control: pd.DataFrame, данные контрольной группы.
        :param data_pilot: pd.DataFrame, данные пилотной группы.
        
        :return (result, length):
            result: float,
                0 - отклоняем H1,
                1 - отклоняем H0,
                0.5 - недостаточно данных для принятия решения
            length: int, сколько потребовалось данных для принятия решения. Если данных 
                недостаточно, то возвращает текущее кол-во данных. Кол-во данных - это
                кол-во элементов в одном из наборов data_control или data_pilot.
                Гарантируется, что они равны.
        """
        # YOUR_CODE_HERE

        if (self.data_pilot_history is None) & (self.data_control_history is None):
            self.data_pilot_history = data_pilot.sort_values(self.time_column_name)
            self.data_control_history = data_control.sort_values(self.time_column_name)

        min_len = min([len(data_control), len(data_pilot)])
        data_one = data_control[:min_len][self.metric_name]
        data_two = data_pilot[:min_len][self.metric_name]
        delta_data = data_two - data_one

        pdf_one_values = self.pdf_one(delta_data)
        pdf_two_values = self.pdf_two(delta_data)

        z = np.cumsum(np.log(pdf_two_values / pdf_one_values))

        indexes_lower = np.arange(min_len)[z < self.lower_bound]
        indexes_upper = np.arange(min_len)[z > self.upper_bound]

        first_index_lower = indexes_lower[0] if len(indexes_lower) > 0 else min_len + 1
        first_index_upper = indexes_upper[0] if len(indexes_upper) > 0 else min_len + 1

        if first_index_lower < first_index_upper:
            return 0, first_index_lower + 1
        elif first_index_lower > first_index_upper:
            return 1, first_index_upper + 1
        else:
            return 0.5, min_len

    def add_data(self, data_control, data_pilot):
        """
        Добавляет новые данные, проверяет гипотезу о равенстве средних.

        Гарантируется, что данные новые и не дублируют ранее добавленные.

        :param data_control: pd.DataFrame, новые данные контрольной группы.
        :param data_pilot: pd.DataFrame, новые данные пилотной группы.

        :return (result, length):
            result: float,
                0 - отклоняем H1,
                1 - отклоняем H0,
                0.5 - недостаточно данных для принятия решения
            length: int, сколько потребовалось данных для принятия решения. Если данных 
                недостаточно, то возвращает текущее кол-во данных. Кол-во данных - это
                кол-во элементов в одном из наборов data_control или data_pilot.
                Гарантируется, что они равны.
        """
        # YOUR_CODE_HERE
        data_control = data_control.sort_values(self.time_column_name)
        data_pilot = data_pilot.sort_values(self.time_column_name)

        self.data_control_history = pd.concat([self.data_control_history, data_control], ignore_index=True)
        self.data_pilot_history = pd.concat([self.data_pilot_history, data_pilot], ignore_index=True)

        return self.run_test(self.data_control_history, self.data_pilot_history)

