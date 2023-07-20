import numpy as np
import pandas as pd


def calculate_linearized_metric(
    df, value_name, user_id_name, list_user_id, date_name, period, metric_name, kappa=None
):
    """
    Вычисляет значение линеаризованной метрики для списка пользователей в определённый период.
    
    df - pd.DataFrame, датафрейм с данными
    value_name - str, название столбца со значениями для вычисления целевой метрики
    user_id_name - str, название столбца с идентификаторами пользователей
    list_user_id - List[int], список идентификаторов пользователей, для которых нужно посчитать метрики
    date_name - str, название столбца с датами
    period - dict, словарь с датами начала и конца периода, за который нужно посчитать метрики.
        Пример, {'begin': '2020-01-01', 'end': '2020-01-08'}. Дата начала периода входит в
        полуинтервал, а дата окончания нет, то есть '2020-01-01' <= date < '2020-01-08'.
    metric_name - str, название полученной метрики
    kappa - float, коэффициент в функции линеаризации.
        Если None, то посчитать как ratio метрику по имеющимся данным.

    return - pd.DataFrame, со столбцами [user_id_name, metric_name], кол-во строк должно быть равно
        кол-ву элементов в списке list_user_id.
    """
    # YOUR_CODE_HERE
    start_date = period['begin']
    end_date = period['end']
    
    df_fil = df[
        (df[date_name] >= start_date) 
        & (df[date_name] < end_date)
        & (df[user_id_name].isin(list_user_id))
        ]
    all_users = pd.DataFrame(data=list_user_id, columns=[user_id_name])
    df_filtered = pd.merge(all_users, df_fil, how='left', on=user_id_name)
    
    df_count_metric = df_filtered.groupby(user_id_name).agg({value_name: 'count'}).rename(columns={value_name: f'{value_name}_count'}).reset_index()
    df_sum_metric = df_filtered.groupby(user_id_name).agg({value_name: 'sum'}).rename(columns={value_name: f'{value_name}_sum'}).reset_index()
    df_lin = pd.merge(df_sum_metric, df_count_metric, how='inner', on=user_id_name).fillna(0)
    
    if kappa is None:
        kappa = np.sum(df_lin[f'{value_name}_sum']) / np.sum(df_lin[f'{value_name}_count'])
    df_lin[metric_name] = df_lin[f'{value_name}_sum'] - kappa * df_lin[f'{value_name}_count']
    return df_lin[[user_id_name, metric_name]]