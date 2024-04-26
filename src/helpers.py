import numpy as np
from src.effect_calculator import ConditionalEffectCalculator, RandomEffectCalculator
import pandas as pd
from src.distribution import DISTRIBUTIONS


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


def draw_datetime(start_date, end_date, size=1):
    start_u = int(pd.Timestamp(start_date).timestamp())
    end_u = int(pd.Timestamp(end_date).timestamp())
    random_datetimes = np.random.randint(start_u, end_u, size)
    return pd.to_datetime(random_datetimes, unit='s')
