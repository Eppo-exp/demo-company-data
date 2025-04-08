import argparse

import numpy as np
import yaml

from src.data_simulator import DataSimulator
from src.snowflake_connector import SnowflakeConnector

PROFILE_FILE_PATH = 'local/profile.yml'

parser = argparse.ArgumentParser(description='Simulate experimentation data')
parser.add_argument('use_case_file', metavar='use-case-file', type=str, help='A path to a use case yaml file')
args = parser.parse_args()

# Setting the seed so that results are consistent across runs
np.random.seed(777)

with open(PROFILE_FILE_PATH) as file:
    profile = yaml.safe_load(file)

with open(args.use_case_file, 'r') as file:
    config = yaml.safe_load(file)

generator = DataSimulator(config)
generator.simulate()
generator.log_data_summary()

snowflake_connector = SnowflakeConnector(**profile)
generator.push_to_snowflake(snowflake_connector)
