import numpy as np
import pandas as pd

from src.distribution import DISTRIBUTIONS
from src.effect_calculator import ConditionalEffectCalculator, RandomEffectCalculator


def draw_from_data_and_configs(data, config):
    distribution_type = DISTRIBUTIONS[config['type']]

    parameter_values = {}

    for parameter, parameter_config in config['parameters'].items():
        parameter_values[parameter] = parameter_config['baseline_value'] * np.ones(len(data))

        if 'conditional_effects' in parameter_config:
            parameter_values[parameter] += ConditionalEffectCalculator(data,
                                                                       parameter_config['conditional_effects']
                                                                       ).get_effects()

        if 'random_effects' in parameter_config:
            parameter_values[parameter] += RandomEffectCalculator(data,
                                                                  parameter_config['random_effects']
                                                                  ).get_effects()

    return distribution_type(parameter_values).draw()


def format_column_name(x):
    return x.replace(' ', '_').lower()


def duplicate_rows(df, frequency):
    return df.loc[df.index.repeat(frequency)].reset_index(drop=True)


def draw_datetime(start_dates, end_dates):
    ONE_BILLION = 10 ** 9
    start_timestamps = pd.to_datetime(start_dates).astype(int) // ONE_BILLION
    end_timestamps = pd.to_datetime(end_dates).astype(int) // ONE_BILLION

    return pd.to_datetime(np.random.randint(start_timestamps, end_timestamps), unit='s')
