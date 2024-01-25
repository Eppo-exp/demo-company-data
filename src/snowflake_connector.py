
class SnowflakeConnector:
    def init():
        # check for environment variables (otherwise check for dbt config file?)
        pass

    def push_table(table_name, table_data):
        # push {table_data} to {self.snowflake_warehouse}.{self.snowflake_table}.{table_name}