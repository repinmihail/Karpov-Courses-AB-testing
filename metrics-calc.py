import numpy as np
import pandas as pd


def calculate_sales_metrics(df, cost_name, date_name, sale_id_name, period, filters=None):
    """Вычисляет метрики по продажам.
    
    df - pd.DataFrame, датафрейм с данными. Пример
        pd.DataFrame(
            [[820, '2021-04-03', 1, 213]],
            columns=['cost', 'date', 'sale_id', 'shop_id']
        )
    cost_name - str, название столбца с стоимостью товара
    date_name - str, название столбца с датой покупки
    sale_id_name - str, название столбца с идентификатором покупки (в одной покупке может быть несколько товаров)
    
    period - dict, словарь с датами начала и конца периода пилота.
        Пример, {'begin': '2020-01-01', 'end': '2020-01-08'}.
        Дата начала периода входит в полуинтервал, а дата окончания нет,
        то есть '2020-01-01' <= date < '2020-01-08'.
    
    filters - dict, словарь с фильтрами. Ключ - название поля, по которому фильтруем, значение - список значений,
        которые нужно оставить. Например, {'user_id': [111, 123, 943]}.
        Если None, то фильтровать не нужно.

    return - pd.DataFrame, в индексах все даты из указанного периода отсортированные по возрастанию, 
        столбцы - метрики ['revenue', 'number_purchases', 'average_check', 'average_number_items'].
        Формат данных столбцов - float, формат данных индекса - datetime64[ns].
    """
    start_date = period['begin']
    end_date = period['end']
    calendar = pd.date_range(start_date, end_date, freq = "D").to_frame(name=date_name, index=False)
    calendar_mod = calendar.iloc[:len(calendar) - 1, :]
    
    if filters:
        for key, val in filters.items():
            df = df[df[key].isin(val)]
    
    df_sort = df[(df[date_name] >= start_date) & (df[date_name] < end_date)].sort_values(date_name)

    revenue_by_date = df_sort.groupby(date_name).agg({cost_name: 'sum'}).rename(columns={cost_name: 'revenue'})
    
    number_purchases_by_date = df_sort.groupby(date_name)[sale_id_name].nunique().to_frame().rename(columns={sale_id_name: 'number_purchases'})
    
    average_check_by_purchase = df_sort.groupby([date_name, sale_id_name]).agg({cost_name: 'sum'}).reset_index()[[date_name, cost_name]].set_index(date_name).rename(columns={cost_name: 'average_check'})
    average_check_by_date = average_check_by_purchase.groupby(date_name).mean()
    
    average_number_items_by_purchase = df_sort.groupby([date_name, sale_id_name]).agg({sale_id_name: 'count'}).rename(columns={sale_id_name: 'average_number_items'})
    average_number_items_by_date = average_number_items_by_purchase.groupby(date_name).mean()
    
    full_data = pd.concat([revenue_by_date, number_purchases_by_date, average_check_by_date, average_number_items_by_date], axis=1).reset_index()
    full_data[date_name] = pd.to_datetime(full_data[date_name])
    
    res_ = pd.merge(calendar_mod, full_data, how='left', on=date_name)
    res = res_.set_index(date_name).fillna(0)
    
    return res