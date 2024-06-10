import yaml

from data_simulator import DataSimulator
from snowflake_connector import SnowflakeConnector

profile_file_path = 'local/profile.yml'

with open(profile_file_path) as file:
    profile = yaml.safe_load(file)

with open('use-cases/showcasing_cuped.yml', 'r') as file:
    config = yaml.safe_load(file)

generator = DataSimulator(config)
generator.simulate()
generator.log_data_summary()

snowflake_connector = SnowflakeConnector(**profile)
generator.push_to_snowflake(snowflake_connector)
