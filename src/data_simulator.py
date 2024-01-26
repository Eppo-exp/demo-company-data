import yaml
import random
import pandas as pd
import yaml
import numpy as np
from itertools import chain
from datetime import datetime, timedelta

def to_under_case(x):
    return x.replace(' ', '_').lower()

class DataSimulator:
    def __init__(self, config):
        self.config = config
        self.sample_size = self.config.get('sample_size', 1000)
        self.entity_name = self.config['entity_name']
        self.experiments = self.config.get('experiments', {})
        self.dimensions = self.config.get('dimensions', {})
        self.fact_sources = self.config.get('fact_sources')

        self.entity_column = self.entity_name.lower() + '_id'

    def generate_subjects(self):
        
        self.subjects = []

        for _ in range(self.sample_size):
            subject = {}
            subject[self.entity_column] = _
            for dim_id, dim_info in self.dimensions.items():
                subject[dim_id] = random.choices(
                    population=[var['id'] for var in dim_info['values']],
                    weights=[var['weight'] for var in dim_info['values']]
                )[0]
        
            self.subjects.append(subject)

    def generate_assignments(self):
        
        assignments_data = []
        for _ in range(self.sample_size):

            for exp_id, exp_info in self.experiments.items():
                assignment = {}

                start_date = exp_info['start_date']
                end_date = exp_info['end_date']

                assignment[self.entity_column] = _
                
                assignment['date'] = (
                    start_date + 
                    timedelta(days=random.randint(0, (end_date - start_date).days))
                ).strftime('%Y-%m-%d')
                
                assignment['experiment'] = exp_id

                assignment['variant'] = random.choices(
                    population=[var['id'] for var in exp_info['variants']],
                    weights=[var.get('weight', 1) for var in exp_info['variants']]
                )[0]

                # add dimensional data
                assignment.update(self.subjects[_])

                assignments_data.append(assignment)
        
        self.assignments = assignments_data
    
    def get_active_experiments(self, date, _):
        live_experiments = [
            exp_id
            for exp_id, exp_info in self.experiments.items() 
            if exp_info['start_date'] <= date.date() and exp_info['end_date'] >= date.date()
        ]
        enrolled_experiments = [
            a
            for a in self.assignments
            if a[self.entity_column] == _
                and datetime.strptime(a['date'], '%Y-%m-%d') <= date
                and a['experiment'] in live_experiments
        ]
        return enrolled_experiments

    def evaluate_conditions(self, conditions, subject, active_experiments):
        parameter = 0
        for condition in conditions:

            if 'cond' not in condition:
                parameter += condition['effect']
            
            else:
                included = True
                for cond in condition['cond']:

                    if cond['type'] == 'experiment':

                        if len(active_experiments) == 0:
                            included = False
                        
                        else:
                            exp_var = [
                                a['variant'] 
                                for a in active_experiments 
                                if a['experiment'] == cond['experiment']
                            ]
                            
                            if len(exp_var) == 0:
                                included = False
                            
                            elif exp_var[0] != cond['variant']:
                                included = False
                        
                    if cond['type'] == 'dimension':
                        if subject[0][cond['id']] != cond['value']:
                            included = False

                if included:
                    parameter += condition['effect'] 

        return parameter

    def compute_subject_params(self):
        
        # for each subject:
        #    get dimension values
        #    for each day:
        #       get experiment variant status 
        #       for each metric:
        #           ...compute model parameters (function of experiment variants, dimension values)
        #           simulate metric
        #           append to data if value > 0

        # create date array
        date_array = pd.date_range(
            start=self.config['start_date'], 
            end=self.config['end_date']
        )

        # list of fact sources
        self.fact_source_daily_params = {}

        # for each fact source
        for fact_source_id, fact_source_info in self.fact_sources.items():

          subject_params_daily = []

          # for each subject
          for _ in range(self.sample_size):

              # get dimension values
              _subject = [u for u in self.subjects if u[self.entity_column] == _]

              # for each day
              for date in date_array:

                  # get active experiments
                  active_experiments = self.get_active_experiments(date, _)

                  # compute frequency
                  _lambda = self.evaluate_conditions(
                    fact_source_info['frequency'],
                    _subject, 
                    active_experiments
                  )

                  fact_params = {
                    "frequency": _lambda,
                    "fact_values": []
                  }

                  for fact in fact_source_info['fact_values']:
                      fact_value_params = {
                        "name": fact["name"],
                        "model": fact['model'],
                      }

                      for param_id, param_info in fact['params'].items():

                          param_value = self.evaluate_conditions(
                              param_info,
                              _subject, 
                              active_experiments
                          )

                          fact_value_params[param_id] = param_value

                      fact_params['fact_values'].append(fact_value_params)

                  # append
                  subject_params_daily.append(
                      {
                          self.entity_column: _,
                          'date': date,
                          'fact_params': fact_params
                      }
                  )
 
          self.fact_source_daily_params[fact_source_id] = subject_params_daily

    def simulate_fact(self, fact_params, subject_id, date):

        fact_events = []

        fact_count = np.random.poisson(fact_params['frequency'], 1)

        for i in range(fact_count[0]):

          fact_event = {'date': date}
          fact_event[self.entity_column] = subject_id

          for fact in fact_params['fact_values']:
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


      

    def simulate_facts(self):

      self.fact_source_tables = {}

      for fact_source_id, fact_source_param_info in generator.fact_source_daily_params.items():

        fact_source_data = []
        for fsdp in fact_source_param_info:
          fdsp_sim = self.simulate_fact(
              fsdp['fact_params'],
              fsdp[self.entity_column],
              fsdp['date']
            )
          if len(fdsp_sim):
            fact_source_data.append(fdsp_sim)
        
        self.fact_source_tables[fact_source_id] = list(chain(*fact_source_data))

    

# Sample YAML content
yaml_content = """
sample_size: 10
start_date: 2023-01-01
end_date: 2023-12-31
entity_name: User
dimensions:
  user_persona:
    name: User Persona
    values:
      - id: designer
        name: Designer
        weight: 0.5
      - id: casual_user
        name: Casual User
        weight: 0.5
  device_type:
    name: Device Type
    values:
      - id: ios
        name: iOS
        weight: 0.25
      - id: android
        name: Android
        weight: 0.25
      - id: web
        name: Web
        weight: 0.5
  device_type:
    name: Device Type
    values:
      - id: ios
        name: iOS
        weight: 0.5
      - id: android
        name: Android
        weight: 0.5
experiments:
    new_onboarding:
        name: New Onboarding
        start_date: 2023-03-01
        end_date: 2023-05-29
        variants:
          - id: control
            name: Control
            weight: 0.5
          - id: test
            name: Test
            weight: 0.5
    search_ranking_algorithm:
        name: Search Ranking Algorithm
        start_date: 2023-05-01
        end_date: 2023-08-29
        variants:
          - id: control
            name: Control
            weight: 0.33
          - id: xgboost
            name: XGBoost
            weight: 0.33
          - id: neural_net
            name: Neural Network
            weight: 0.34
metrics:
  revenue:
    name: Revenue
    model: poisson_normal
    params:
      lambda:
        - effect: 1
        - effect: 0.05
          cond:
            - type: experiment
              experiment: new_onboarding
              variant: test
        - effect: -0.15
          cond:
            - type: experiment
              experiment: new_onboarding
              variant: test
            - type: dimension
              id: user_persona
              value: designer
"""

with open('use-cases/dev_model_v2.yml', 'r') as file:
  config = yaml.safe_load(file)

generator = DataSimulator(config)
generator.generate_subjects()
generator.generate_assignments()
generator.compute_subject_params()
generator.simulate_facts()

print('SUBJECT -------------------')
print(pd.DataFrame(generator.subjects))
print('ASSIGNMENTS -------------------')
print(pd.DataFrame(generator.assignments))
print('REVENUE -------------------')
print(pd.DataFrame(generator.fact_source_tables['revenue']))
print('SUPPORT ISSUES -------------------')
print(pd.DataFrame(generator.fact_source_tables['support_tickets']))
