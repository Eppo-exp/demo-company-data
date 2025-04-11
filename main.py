import argparse

import yaml

from src.analysis_sync import AnalysisSync
from src.api_helper import EppoAPIHelper
from src.config_parser import ConfigParser
from src.data_simulator import DataSimulator
from src.snowflake_connector import SnowflakeConnector

PROFILE_FILE_PATH = 'local/profile.yml'
start_date_override = '2024-10-18'

parser = argparse.ArgumentParser(description='Simulate experimentation data')
parser.add_argument('use_case_file', metavar='use-case-file', type=str, help='A path to a use case yaml file')
args = parser.parse_args()

with open(PROFILE_FILE_PATH) as file:
    profile = yaml.safe_load(file)

config_parser = ConfigParser.from_file(args.use_case_file, start_date_override)

generator = DataSimulator(config_parser)
generator.simulate()
generator.log_data_summary()

snowflake_connector = SnowflakeConnector(**profile)
generator.push_to_snowflake(snowflake_connector)

api_helper = EppoAPIHelper()
analysis_sync = AnalysisSync(config_parser, api_helper)
analysis_sync.sync_experiments()
