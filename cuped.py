import numpy as np
import pandas as pd


def calculate_metric(
    df, value_name, user_id_name, list_user_id, date_name, period, metric_name
):
    """
    Вычисляет значение метрики для списка пользователей в определённый период.
    
    df - pd.DataFrame, датафрейм с данными
    value_name - str, название столбца со значениями для вычисления целевой метрики
    user_id_name - str, название столбца с идентификаторами пользователей
    list_user_id - List[int], список идентификаторов пользователей, для которых нужно посчитать метрики
    date_name - str, название столбца с датами
    period - dict, словарь с датами начала и конца периода, за который нужно посчитать метрики.
        Пример, {'begin': '2020-01-01', 'end': '2020-01-08'}. Дата начала периода входит нужный
        полуинтервал, а дата окончание нет, то есть '2020-01-01' <= date < '2020-01-08'.
    metric_name - str, название полученной метрики

    return - pd.DataFrame, со столбцами [user_id_name, metric_name], кол-во строк должно быть равно
        кол-ву элементов в списке list_user_id.
    """
    # YOUR_CODE_HERE
    start_date = period['begin']
    end_date = period['end']
    
    df_user_filter = df[df[user_id_name].isin(list_user_id)]
    
    df_date_filter = df_user_filter[
        (df_user_filter[date_name] >= start_date) & (df_user_filter[date_name] < end_date)
        ]
    
    purchase_by_user = df_date_filter.groupby(user_id_name).agg({value_name: 'sum'}).rename(columns={value_name: metric_name}).reset_index()
    all_users_purchases = pd.DataFrame(data=list_user_id, columns=[user_id_name])
    res = pd.merge(all_users_purchases, purchase_by_user, how='left', on=user_id_name).fillna(0)
    return res

def calculate_metric_cuped(
    df, value_name, user_id_name, list_user_id, date_name, periods, metric_name
):
    """
    Вычисляет метрики во время пилота, коварианту и преобразованную метрику cuped.
    
    df - pd.DataFrame, датафрейм с данными
    value_name - str, название столбца со значениями для вычисления целевой метрики
    user_id_name - str, название столбца с идентификаторами пользователей
    list_user_id - List[int], список идентификаторов пользователей, для которых нужно посчитать метрики
    date_name - str, название столбца с датами
    periods - dict, словарь с датами начала и конца периода пилота и препилота.
        Пример, {
            'prepilot': {'begin': '2020-01-01', 'end': '2020-01-08'},
            'pilot': {'begin': '2020-01-08', 'end': '2020-01-15'}
        }.
        Дата начала периода входит в полуинтервал, а дата окончания нет,
        то есть '2020-01-01' <= date < '2020-01-08'.
    metric_name - str, название полученной метрики

    return - pd.DataFrame, со столбцами
        [user_id_name, metric_name, f'{metric_name}_prepilot', f'{metric_name}_cuped'],
        кол-во строк должно быть равно кол-ву элементов в списке list_user_id.
    """
    prepilot_period = periods['prepilot']    
    pilot_period = periods['pilot']
    
    prepilot_df = calculate_metric(df, value_name, user_id_name, list_user_id, date_name, prepilot_period, metric_name)
    pilot_df = calculate_metric(df, value_name, user_id_name, list_user_id, date_name, pilot_period, metric_name)    
    
    def calculate_theta(y_prepilot_cov, y_pilot) -> float:
        """
        Вычисляем Theta.
        
        y_control - значения метрики во время пилота на контрольной группе
        y_pilot - значения метрики во время пилота на пилотной группе
        y_control_cov - значения ковариант на контрольной группе (той же самой метрики, но на препилоте)
        y_pilot_cov - значения ковариант на пилотной группе
        """
        #y = np.hstack([y_control, y_pilot])
        #y_cov = np.hstack([y_control_cov, y_pilot_cov])
        covariance = np.cov(y_prepilot_cov, y_pilot)[0, 1]
        variance = np.var(y_prepilot_cov)
        theta = covariance / variance
        return theta
    
    theta = calculate_theta(prepilot_df[metric_name], pilot_df[metric_name])
    #res = pd.concat([pilot_df, prepilot_df], axis=1)
    res = pd.merge(pilot_df, prepilot_df, how='inner', on=user_id_name)
    res.columns = [user_id_name, metric_name, f'{metric_name}_prepilot']
    res[f'{metric_name}_cuped'] = res[metric_name] - theta * res[f'{metric_name}_prepilot']
    
    return res