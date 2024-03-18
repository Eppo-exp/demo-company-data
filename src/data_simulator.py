import yaml
import random
import pandas as pd
import yaml
import numpy as np
from itertools import chain, product
from datetime import datetime, timedelta
import logging
from snowflake_connector import SnowflakeConnector
from time import time

console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

logger = logging.getLogger(__name__)
logger.level = logging.INFO
logger.addHandler(console_handler)
logger.propagate = False


def to_under_case(x):
    return x.replace(' ', '_').lower()


def evaluate_condition(df, conditions):
    parameters = np.zeros(len(df))
    for condition in conditions:
        if 'cond' not in condition:
            parameters += condition['effect']

        else:
            # Initially assume everyone is included, exclude them if they fail to meet a condition
            included = np.ones(len(df), dtype=bool)
            for cond in condition['cond']:
                if cond['type'] == 'experiment':
                    variant_column = f"{cond['experiment']}_assignment"
                    included &= (df[variant_column] == cond['variant'])

                if cond['type'] == 'dimension':
                    included &= (df[cond['id']] == cond['value'])

            parameters += condition['effect'] * included.values

    return parameters


def simulate_fact(x, param_feild, entity_column):
    fact_events = []
    fact_params = x.get(param_feild)

    fact_count = np.random.poisson(fact_params['frequency'], 1)

    for i in range(fact_count[0]):

        fact_event = {'date': x['date']}
        fact_event[entity_column] = x[entity_column]

        for fact in fact_params['values']:

            if fact['model'] == 'normal':
                sim_value = np.random.normal(fact['mu'], fact['sigma'], 1)[0]

            elif fact['model'] == 'bernoulli':
                sim_value = np.random.binomial(1, fact['rate'], 1)[0]
                if sim_value == 0:
                    sim_value = None

            else:
                raise Exception('Invalid fact model: ' + fact['model'])

            fact_event[to_under_case(fact['name'])] = sim_value

        fact_events.append(fact_event)

    return fact_events


class DataSimulator:
    def __init__(self, config):
        self.config = config
        self.sample_size = self.config.get('sample_size', 1000)
        self.entity_name = self.config['entity_name']
        self.experiments = self.config.get('experiments', {})
        self.dimensions = self.config.get('dimensions', {})
        self.fact_sources = self.config.get('fact_sources')
        self.entity_column = self.entity_name.lower() + '_id'

    # utility function to get a merge-able data frame
    def experiment_dates(self):
        x = {'experiment': [], 'experiment_end_date': []}
        for experiment_name, details in self.experiments.items():
            x['experiment'].append(experiment_name)
            x['experiment_end_date'].append(details['end_date'])
        return pd.DataFrame(x)

    def generate_subjects(self):

        simulated_dimensions = {
            dim_id: np.random.choice(
                a=[var['id'] for var in dim_info['values']],
                p=[var['weight'] for var in dim_info['values']],
                size=self.sample_size
            ) for dim_id, dim_info in self.dimensions.items()
        }

        self.subjects = pd.DataFrame({
            self.entity_column: np.arange(self.sample_size),
            **simulated_dimensions
        })

    def _create_assignment_df_for_experiment(self, exp_id):
        exp_info = self.experiments[exp_id]
        start_date = exp_info['start_date']
        end_date = exp_info['end_date']

        assignment_weights = np.array([var.get('weight', 1) for var in exp_info['variants']])
        assigment_probabilities = assignment_weights / assignment_weights.sum()

        experiment_assignment = pd.DataFrame({
            self.entity_column: np.arange(self.sample_size),
            'start_date': start_date,
            'end_date': end_date,
            'experiment': exp_id,
            'variant': np.random.choice(
                a=[var['id'] for var in exp_info['variants']],
                p=assigment_probabilities,
                size=self.sample_size
            )
        })
        date_offsets = np.random.randint(0, (end_date - start_date).days, size=self.sample_size)
        experiment_assignment['date'] = (
                pd.to_datetime(experiment_assignment['start_date']) +
                pd.to_timedelta(date_offsets, unit='D')
        )
        return experiment_assignment

    # to do: create as data frame
    def generate_assignments(self):
        self.assignments = pd.concat(
            [self._create_assignment_df_for_experiment(exp_id) for exp_id in self.experiments.keys()]
        )

    def _get_active_experiments(self):
        active_experiments = self.daily_subject_params.merge(
            pd.DataFrame(self.assignments),
            on='user_id',
            suffixes=['', '_assigned']
        )

        active_experiments = active_experiments.merge(
            self.experiment_dates(),
            on='experiment'
        )

        date_mask = \
            (active_experiments['date_assigned'] \
             <= active_experiments['date']) \
            & (active_experiments['date'] \
               <= active_experiments['experiment_end_date'])

        # First, create a pivot table as before.
        active_experiments = active_experiments[date_mask].pivot_table(
            index=[self.entity_column, 'date'],
            columns='experiment',
            values='variant',
            aggfunc='first'
        )

        active_experiments.columns = [f"{column}_assignment" for column in active_experiments.columns]
        active_experiments = active_experiments.reset_index()
        return active_experiments

    def get_subject_params_inputs(self):

        self.daily_subject_params = pd.DataFrame(
            list(product(
                pd.date_range(start=self.config['start_date'], end=self.config['end_date']),
                range(self.sample_size)
            )),
            columns=['date', self.entity_column]
        )
        active_experiments = self._get_active_experiments()

        self.daily_subject_params = self.daily_subject_params.merge(
            active_experiments,
            on=[self.entity_column, 'date'],
            how='left'
        )

        self.daily_subject_params = self.daily_subject_params.merge(self.subjects)

    # def compute_subject_params(self):
    #
    #     for fact_source_id, fact_source_info in self.fact_sources.items():
    #         self.daily_subject_params[fact_source_id] = self.daily_subject_params.apply(
    #             evaluate_conditions,
    #             args=(fact_source_info,),
    #             axis=1
    #         )

    def _get_daily_subject_params(self, fact_source_info):
        params = self.evaluate_conditions(fact_source_info)
        x = 3

    def compute_subject_params(self):
        for fact_source_id, fact_source_info in self.fact_sources.items():
            self.daily_subject_params[fact_source_id] = self._get_daily_subject_params(fact_source_info)

    def evaluate_conditions(self, fact_source_info):
        freq = evaluate_condition(self.daily_subject_params, fact_source_info['frequency'])





        fv_params = {'frequency': freq, "values": []}

        for fv in fact_source_info['fact_values']:

            if fv['model'] == 'normal':
                mu = evaluate_condition(self.daily_subject_params, fv['params']['mu'])
                sigma = evaluate_condition(self.daily_subject_params, fv['params']['sigma'])

                fv_params['values'].append({
                    'name': fv['name'],
                    'model': fv['model'],
                    'mu': mu,
                    'sigma': sigma
                })

            elif fv['model'] == 'bernoulli':
                rate = evaluate_condition(self.daily_subject_params, fv['params']['rate'])
                fv_params['values'].append({
                    'name': fv['name'],
                    'model': fv['model'],
                    'rate': rate
                })

            else:
                raise Exception('invalid fact value model: ' + fv['model'])

        return fv_params

    # def simulate_facts(self):
    #
    #     self.fact_source_tables = {}
    #
    #     for fact_source_id, fact_source_info in self.config['fact_sources'].items():
    #         fact_source_data = self.daily_subject_params.apply(
    #             simulate_fact,
    #             args=(fact_source_id, self.entity_column),
    #             axis=1
    #         )
    #
    #         self.fact_source_tables[fact_source_id] = pd.DataFrame(
    #             list(chain(*fact_source_data))
    #         )

    # def simulate_facts(self):
    #     fact_source = 'revenue'
    #     fact_source_info = self.fact_sources[fact_source]
    #     for fact

    def simulate(self):

        logger.info('generating subjects')
        self.generate_subjects()

        logger.info('generating assignments')
        self.generate_assignments()

        logger.info('preparing subject parameter inputs')
        self.get_subject_params_inputs()

        logger.info('computing subject parameters')
        self.compute_subject_params()

        logger.info('simulating facts')
        self.simulate_facts()

    def log_data_summary(self):

        logger.info('assignments')
        logger.info(print(pd.DataFrame(self.subjects)))

        for fact_source_table_id, fact_source_data in self.fact_source_tables.items():
            logger.info(fact_source_table_id)
            logger.info(fact_source_data)

    def push_to_snowflake(self):

        logger.info('connecting to Snowflake')
        snowflake_connection = SnowflakeConnector()

        logger.info('pushing assignments table')
        snowflake_connection.push_table(
            'assignments',
            pd.DataFrame(self.assignments)
        )

        for fact_source_table_id, fact_source_data in self.fact_source_tables.items():
            logger.info('pushing ' + fact_source_table_id + ' table')
            snowflake_connection.push_table(
                fact_source_table_id,
                fact_source_data
            )
