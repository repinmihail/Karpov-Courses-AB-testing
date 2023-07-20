import numpy as np
import pandas as pd
from scipy.stats import ttest_ind


def estimate_second_type_error(df_pilot_group, df_control_group, metric_name, effects, alpha=0.05, n_iter=10000, seed=None):
    """Оцениваем ошибки второго рода.

    Бутстрепим выборки из пилотной и контрольной групп тех же размеров, добавляем эффект к пилотной группе,
    считаем долю случаев без значимых отличий.
    
    df_pilot_group - pd.DataFrame, датафрейм с данными пилотной группы
    df_control_group - pd.DataFrame, датафрейм с данными контрольной группы
    metric_name - str, названия столбца с метрикой
    effects - List[float], список размеров эффектов ([1.03] - увеличение на 3%).
    alpha - float, уровень значимости для статтеста
    n_iter - int, кол-во итераций бутстрапа
    seed - int or None, состояние генератора случайных чисел

    return - dict, {размер_эффекта: ошибка_второго_рода}
    """
    # YOUR_CODE_HERE
    np.random.seed(seed)
    
    
    a_bootstrap = np.random.choice(
        df_control_group.loc[:,metric_name].to_numpy().ravel(), 
        size=(len(df_control_group), n_iter)
        )
    b_bootstrap = np.random.choice(
        df_pilot_group.loc[:,metric_name].to_numpy().ravel(), 
        size=(len(df_pilot_group), n_iter)
        )
    
    res_dict = {}
    for eff in effects:
        true_positive_tt = []
        for i in range(n_iter):
            a_sample = pd.DataFrame(a_bootstrap).loc[:,i]
            b_sample = pd.DataFrame(b_bootstrap).loc[:,i] * eff
            
            pvalue_ab_tt = ttest_ind(a_sample, b_sample)[1]
            true_positive_tt.append(int(pvalue_ab_tt < alpha)) # Фиксируем ошибки II рода
        res_dict[eff] = 1 - np.mean(true_positive_tt)
    return res_dict