import numpy as np
def get_bernoulli_confidence_interval(values: np.array):
    """Вычисляет доверительный интервал для параметра распределения Бернулли.

    :param values: массив элементов из нулей и единиц.
    :return (left_bound, right_bound): границы доверительного интервала.
    """
    left_bound = np.mean(values) - 1.96 * np.std(values) / np.sqrt(len(values))
    
    if left_bound < 0: left_bound = 0
    
    right_bound = np.mean(values) + 1.96 * np.std(values) / np.sqrt(len(values))
    
    if right_bound > 1: right_bound = 1
        
    return left_bound, right_bound