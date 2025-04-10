import pandas as pd

from src.helpers import draw_from_data_and_configs, duplicate_rows, draw_datetime


class FactSourceBuilder:
    def __init__(self, assignment_df, fact_source_configs, entity):
        self.assignment_df = assignment_df
        self.fact_source_configs = fact_source_configs
        self.entity = entity

    def simulate(self):
        fact_frequency = draw_from_data_and_configs(self.assignment_df,
                                                    self.fact_source_configs['frequency_distribution'])

        # Makes it so each assignment is duplicated the number of times corresponding to each fact frequency
        # This makes it easy to calculate conditional effects in a vectorized way
        exploded_assignments = duplicate_rows(self.assignment_df, fact_frequency)
        fact_values = {
            self.entity: exploded_assignments[self.entity],
            'event_timestamp': draw_datetime(exploded_assignments['date'], exploded_assignments['end_date']),
            **{
                fv['name']: draw_from_data_and_configs(exploded_assignments, fv['distribution'])
                for fv in self.fact_source_configs['fact_values']
            }
        }

        return pd.DataFrame(fact_values)
