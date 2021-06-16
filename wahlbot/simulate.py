from typing import Dict
import numpy as np
import random


def simulate_progress(progress: Dict, init: bool) -> Dict:
    if init:
        simulation = {elem: 0 for elem in progress.keys()}
    else:
        simulation = {key: add_random_int(value) for key, value in progress.items()}
    return simulation


def simulate_data(data, cfg):
    data[cfg['DIFF']] = np.random.randint(-20, 20, len(data))
    data[cfg['DIFF_TURNOUT']] = np.random.randint(-20, 20, len(data))
    data[cfg['PERCENT_PREELECTION']] = np.random.randint(0, 38, len(data))
    data[cfg['INVALID_VOTES']] = np.random.randint(0, 38, len(data))

    data = data.groupby(cfg['CONSTITUENCY']).apply(set_random_int, [cfg['INVALID_VOTES']])
    data = data.groupby(cfg['CONSTITUENCY']).apply(set_random_int, [cfg['DIFF']])
    data[cfg['PERCENT']] = np.random.randint(0, 38, len(data))
    return data


def add_random_int(value: int, max_int: int = 25) -> int:
    new_value = value + random.randint(0, 5)
    if new_value > max_int:
        new_value = max_int
    return new_value


def set_random_int(df, col: str):
    df.loc[:, col] = random.randint(0, 10)
    return df
