# usage:
# python set_local_env.py <path to dbt profile file>

import yaml
import os
import sys
import pandas as pd
from datetime import datetime

script_name = sys.argv[0]
#profile_file_path = sys.argv[1]
profile_file_path = '/Users/lukas/.dbt/profiles.yml'
from data_simulator import DataSimulator
from snowflake_connector import SnowflakeConnector

with open(profile_file_path) as file:
    dbt_profile = yaml.safe_load(file)

os.environ["SNOWFLAKE_ACCOUNT"] = dbt_profile['eppo_snowflake']['outputs']['dev']['account']
os.environ["SNOWFLAKE_USER"] = dbt_profile['eppo_snowflake']['outputs']['dev']['user']
os.environ["SNOWFLAKE_PASSWORD"] = dbt_profile['eppo_snowflake']['outputs']['dev']['password']
os.environ["SNOWFLAKE_WAREHOUSE"]  = dbt_profile['eppo_snowflake']['outputs']['dev']['warehouse']
os.environ["SNOWFLAKE_DATABASE"] = 'customer_db'
os.environ["SNOWFLAKE_SCHEMA"] = 'demo_dev'


with open('use-cases/dev_model_v2.yml', 'r') as file:
  config = yaml.safe_load(file)

generator = DataSimulator(config)
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': creating subjects')
generator.generate_subjects()
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': creating assignments')
generator.generate_assignments()
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': computing subject params')
generator.compute_subject_params()
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': simulating facts')
generator.simulate_facts()

snowflake_connection = SnowflakeConnector()

print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': pushing assignments:')
print(pd.DataFrame(generator.assignments))
snowflake_connection.push_table(
  'assignments', 
  pd.DataFrame(generator.assignments)
)

for fact_source_table_id, fact_source_table_name in generator.fact_source_tables.items():
  print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': pushing ' + fact_source_table_id + ':')
  snowflake_connection.push_table(
    fact_source_table_id, 
    pd.DataFrame(fact_source_table_name)
  )

