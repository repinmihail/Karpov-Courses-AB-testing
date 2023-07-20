import numpy as np
import pandas as pd
from scipy.stats import norm


def estimate_sample_size(df, metric_name, effects, alpha=0.05, beta=0.2):
    """Оцениваем sample size для списка эффектов.

    df - pd.DataFrame, датафрейм с данными
    metric_name - str, название столбца с целевой метрикой
    effects - List[float], список ожидаемых эффектов. Например, [1.03] - увеличение на 3%
    alpha - float, ошибка первого рода
    beta - float, ошибка второго рода

    return - pd.DataFrame со столбцами ['effect', 'sample_size']    
    """
    # YOUR_CODE_HERE
    t_alpha = norm.ppf(1 - alpha / 2, loc=0, scale=1)
    t_beta = norm.ppf(1 - beta, loc=0, scale=1)
    z_scores_sum_squared = (t_alpha + t_beta) ** 2
    mu = np.mean(df[metric_name])
    std = np.std(df[metric_name])
    
    res = []
    for eff in effects:
        epsilon = (eff - 1) * mu
        sample_size = int(
                np.ceil(
                    z_scores_sum_squared * (2 * std ** 2) / (epsilon ** 2)
                )
            )
        res.append((eff, sample_size))
    result = pd.DataFrame(res, columns = ['effect', 'sample_size'])
    return result
    