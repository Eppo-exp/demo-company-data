from data_simulator import DataSimulator
from snowflake_connector import SnowflakeConnector

with open('use-cases/dev_model_v2.yml', 'r') as file:
  config = yaml.safe_load(file)

generator = DataSimulator(config)
generator.simulate()

#snowflake_connection = SnowflakeConnector()
#snowflake_connection.push_table('assignments', pd.DataFrame(generator.assignments))


# create SnowflakeConnector instance
# create EppoSync instance
# for file in use-cases:
#   simulated_data = DataSimulator(file)
#   snowflake_connector.push_table('assignments', simulated_data.assignments)
#   for tbl, tbl_name in self.facts:
#       snowflake_connector.push_table(tbl_name, tbl)