# create SnowflakeConnector instance
# create EppoSync instance
# for file in use-cases:
#   simulated_data = DataSimulator(file)
#   snowflake_connector.push_table('assignments', simulated_data.assignments)
#   for tbl, tbl_name in self.facts:
#       snowflake_connector.push_table(tbl_name, tbl)