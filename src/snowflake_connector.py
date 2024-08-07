import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

from src.helpers import format_column_name


class SnowflakeConnector:
    def __init__(self, **connection_params):
        self.connection = snowflake.connector.connect(
            **connection_params
        )

    def push_table(self, table_name, table_data):
        table_data.columns = [format_column_name(col) for col in table_data.columns]

        table_data.columns = table_data.columns.str.upper()

        write_pandas(
            self.connection,
            df=table_data,
            table_name=table_name.upper(),
            auto_create_table=True,
            use_logical_type=True,
            overwrite=True,
        )

    def close_connection(self):
        # Close the cursor and connection when done
        self.connection.close()
