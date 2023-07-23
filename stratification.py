import numpy as np
import pandas as pd


def select_stratified_groups(data, strat_columns, group_size, weights=None, seed=None):
    """Подбирает стратифицированные группы для эксперимента.

    data - pd.DataFrame, датафрейм с описанием объектов, содержит атрибуты для стратификации.
    strat_columns - List[str], список названий столбцов, по которым нужно стратифицировать.
    group_size - int, размеры групп.
    weights - dict, словарь весов страт {strat: weight}, где strat - либо tuple значений элементов страт,
        например, для strat_columns=['os', 'gender', 'birth_year'] будет ('ios', 'man', 1992), либо просто строка/число.
        Если None, определить веса пропорционально доле страт в датафрейме data.
    seed - int, исходное состояние генератора случайных чисел для воспроизводимости
        результатов. Если None, то состояние генератора не устанавливается.

    return (data_pilot, data_control) - два датафрейма того же формата, что и data
        c пилотной и контрольной группами.
    """
    # YOUR_CODE_HERE
    np.random.seed(seed)
    
    pilot = pd.DataFrame(columns=strat_columns)
    control = pd.DataFrame(columns=strat_columns)
    if weights:
        for strat, weight in weights.items():
            if isinstance(strat, (str, int, float)):
                val_list = []
                val_list += [strat]
            else:
                val_list = list(strat)
            strat_df = data[data[strat_columns].isin(val_list).all(axis=1)].reset_index(drop=True)
            ab_group_size = int(round(group_size * weight))
            random_indexes_ab = np.random.choice([i for i in range(len(strat_df))], ab_group_size * 2, False)
            a_indexes = random_indexes_ab[:ab_group_size]
            b_indexes = random_indexes_ab[ab_group_size:]
            a_random_strata_df = strat_df.iloc[a_indexes,:]
            b_random_strata_df = strat_df.iloc[b_indexes,:]
  
            control = pd.concat([control, a_random_strata_df], ignore_index=True)
            pilot = pd.concat([pilot, b_random_strata_df], ignore_index=True)
    else:
        strat_dict = data.groupby(strat_columns).count().iloc[:,0].to_dict()
        len_data = len(data)
        strat_dict_shares = {strata:share/len_data for (strata, share) in strat_dict.items()}
        for strat, weight in strat_dict_shares.items():
            if isinstance(strat, (str, int, float)):
                val_list = []
                val_list += [strat]
            else:
                val_list = list(strat)
            strat_df = data[data[strat_columns].isin(val_list).all(axis=1)].reset_index(drop=True)
            ab_group_size = int(round(group_size * weight))
            random_indexes_ab = np.random.choice([i for i in range(len(strat_df))], ab_group_size * 2, False)
            a_indexes = random_indexes_ab[:ab_group_size]
            b_indexes = random_indexes_ab[ab_group_size:]
            a_random_strata_df = strat_df.iloc[a_indexes,:]
            b_random_strata_df = strat_df.iloc[b_indexes,:]
   
            control = pd.concat([control, a_random_strata_df], ignore_index=True)
            pilot = pd.concat([pilot, b_random_strata_df], ignore_index=True)
    return (pilot, control)