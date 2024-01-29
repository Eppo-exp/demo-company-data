# usage:
# python set_local_env.py <path to dbt profile file>

import yaml
import os
import sys
import pandas as pd
from datetime import datetime
from data_simulator import DataSimulator

profile_file_path = '/Users/lukas/.dbt/profiles.yml'

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
generator.simulate()
generator.log_data_summary()
generator.push_to_snowflake()