import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

def estimate_first_type_error(df_pilot_group, df_control_group, metric_name, alpha=0.05, n_iter=10000, seed=None):
    """Оцениваем ошибку первого рода.

    Бутстрепим выборки из пилотной и контрольной групп тех же размеров, считаем долю случаев с значимыми отличиями.
    
    df_pilot_group - pd.DataFrame, датафрейм с данными пилотной группы
    df_control_group - pd.DataFrame, датафрейм с данными контрольной группы
    metric_name - str, названия столбца с метрикой
    alpha - float, уровень значимости для статтеста
    n_iter - int, кол-во итераций бутстрапа
    seed - int or None, состояние генератора случайных чисел.

    return - float, ошибка первого рода
    """
    np.random.seed(seed)
    
    
    a_bootstrap = np.random.choice(
        df_control_group.loc[:,metric_name].to_numpy().ravel(), 
        size=(len(df_control_group), n_iter)
        )
    b_bootstrap = np.random.choice(
        df_pilot_group.loc[:,metric_name].to_numpy().ravel(), 
        size=(len(df_pilot_group), n_iter)
        )
    
    false_positive_tt = []
    for i in range(n_iter):
        a_sample = pd.DataFrame(a_bootstrap).loc[:,i]
        b_sample = pd.DataFrame(b_bootstrap).loc[:,i]
        pvalue_ab_tt = ttest_ind(a_sample, b_sample)[1]
        false_positive_tt.append(int(pvalue_ab_tt < alpha)) # Фиксируем ошибки I рода
    
    return np.mean(false_positive_tt)