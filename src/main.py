import yaml
import os
from data_simulator import DataSimulator

profile_file_path = 'local/profile.yml'

with open(profile_file_path) as file:
    profile = yaml.safe_load(file)


# set local env
# TODO: if not in dev environment, assume these are already set
os.environ["SNOWFLAKE_ACCOUNT"] = profile['account']
os.environ["SNOWFLAKE_USER"] = profile['user']
os.environ["SNOWFLAKE_PASSWORD"] = profile['password']
os.environ["SNOWFLAKE_WAREHOUSE"]  = profile['warehouse']
os.environ["SNOWFLAKE_DATABASE"] = 'customer_db'
os.environ["SNOWFLAKE_SCHEMA"] = 'demo_dev'


with open('use-cases/dev_use_case.yml', 'r') as file:
  config = yaml.safe_load(file)

generator = DataSimulator(config)
from time import time
t1 = time()
generator.simulate()
t2 = time()
print(t2 - t1)
generator.log_data_summary()
# generator.push_to_snowflake()
