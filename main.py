import argparse

import yaml

from src.analysis_sync import AnalysisSync
from src.api_helper import EppoAPIHelper
from src.config_parser import ConfigParser

from src.data_simulator import DataSimulator
from src.snowflake_connector import SnowflakeConnector

PROFILE_FILE_PATH = 'local/profile.yml'

parser = argparse.ArgumentParser(description='Simulate experimentation data')
parser.add_argument('use_case_file', metavar='use-case-file', type=str, help='A path to a use case yaml file')
parser.add_argument('--start-date-override', type=str,
                    help='Override start date (YYYY-MM-DD); shifts all dates in the use case file such that the '
                         'earliest experiment in the file starts on this date')
args = parser.parse_args()

# Setting the seed so that results are consistent across runs
np.random.seed(777)

with open(PROFILE_FILE_PATH) as file:
    profile = yaml.safe_load(file)

config_parser = ConfigParser.from_file(args.use_case_file, args.start_date_override)

generator = DataSimulator(config_parser)
generator.simulate()
generator.log_data_summary()

snowflake_connector = SnowflakeConnector(**profile)
generator.push_to_snowflake(snowflake_connector)

api_helper = EppoAPIHelper()
analysis_sync = AnalysisSync(config_parser, api_helper)
analysis_sync.sync_experiments()
