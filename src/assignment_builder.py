import numpy as np
import pandas as pd
import hashlib

from src.helpers import draw_from_data_and_configs, duplicate_rows


def add_dimension_columns(df, dimensions):
    for dim_id, dim_info in dimensions.items():
        df[dim_id] = np.random.choice(
            a=[var['id'] for var in dim_info['values']],
            p=[var['weight'] for var in dim_info['values']],
            size=len(df)
        )

    return df


def add_assignment_date_column(df):
    date_offsets = np.random.randint(0, (pd.to_datetime(df['end_date']) - pd.to_datetime(df['start_date'])).dt.days)
    df['date'] = (
            pd.to_datetime(df['start_date']) + pd.to_timedelta(date_offsets, unit='D')
    )
    return df


class AssignmentSimulator:
    def __init__(self, entity_name, experiments, dimensions, sample_size=1000):
        self.entity_name = entity_name
        self.experiments = experiments
        self.dimensions = dimensions
        self.sample_size = sample_size

    def _assign_variants_one_experiment(self, exp_id):
        exp_info = self.experiments[exp_id]
        assignment_weights = np.array([var.get('weight', 1) for var in exp_info['variants']])
        assigment_probabilities = assignment_weights / assignment_weights.sum()
        return pd.DataFrame({
            self.entity_name: [hashlib.md5(str(x).encode()).hexdigest() for x in np.arange(self.sample_size)],
            'experiment': exp_id,
            'start_date': exp_info['start_date'],
            'end_date': exp_info['end_date'],
            'variant': np.random.choice(
                a=[var['id'] for var in exp_info['variants']],
                p=assigment_probabilities,
                size=self.sample_size
            )
        })

    def _assign_variants(self):
        return pd.concat(
            [self._assign_variants_one_experiment(exp_id) for exp_id in self.experiments.keys()]
        ).reset_index(drop=True)

    def simulate(self):
        return (self._assign_variants()
                .pipe(add_dimension_columns, self.dimensions['entity'])
                .pipe(add_assignment_date_column)
                )


class ClusteredAssignmentSimulator(AssignmentSimulator):
    def __init__(self, entity_name, subentity_name, experiments, dimensions,
                 cluster_size_distribution, sample_size=1000):
        super().__init__(entity_name, experiments, dimensions, sample_size)
        self.subentity_name = subentity_name
        self.cluster_size_distribution = cluster_size_distribution

    def _draw_cluster_sizes(self, df):
        return draw_from_data_and_configs(df, self.cluster_size_distribution)

    def split_into_subentities(self, df):
        cluster_sizes = self._draw_cluster_sizes(df)

        df = duplicate_rows(df, cluster_sizes)
        
        df[self.subentity_name] = [hashlib.md5(str(x).encode()).hexdigest() for x in np.arange(len(df))]

        return df

    def simulate(self):
        return (self._assign_variants()
                .pipe(add_dimension_columns, self.dimensions['entity'])
                .pipe(self.split_into_subentities)
                .pipe(add_dimension_columns, self.dimensions['subentity'])
                .pipe(add_assignment_date_column)
                )
