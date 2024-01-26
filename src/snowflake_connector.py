import snowflake.connector
import os
import pandas as pd
from snowflake.snowpark.session import Session
from snowflake.connector.pandas_tools import write_pandas


snowflake_data_types = {
    'int64': 'INT',
    'float64': 'FLOAT',
    'object': 'VARCHAR',
    'datetime64[ns]': 'TIMESTAMP'
}

class SnowflakeConnector:
    def __init__(self):
        # check for environment variables
        snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
        snowflake_user = os.getenv("SNOWFLAKE_USER")
        snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
        snowflake_warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        snowflake_database = os.getenv("SNOWFLAKE_DATABASE")
        snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA")

        # create a connection
        self.connection = snowflake.connector.connect(
            user=snowflake_user,
            password=snowflake_password,
            account=snowflake_account,
            warehouse=snowflake_warehouse,
            database=snowflake_database,
            schema=snowflake_schema
        )

        # create a cursor
        self.cursor = self.connection.cursor()

        # store table destination information
        self.snowflake_database = snowflake_database
        self.snowflake_schema = snowflake_schema

    def push_table(self, table_name, table_data):

        #create_table_sql = f"""
        #    CREATE OR REPLACE TABLE {self.snowflake_database}.{self.snowflake_schema}.{table_name} (
        #        DATE DATE,   
        #    """

        #for column_name, data_type in zip(table_data.columns, table_data.dtypes):
        #    if column_name != 'date':
        #        create_table_sql += f"{column_name} {snowflake_data_types[str(data_type)]}, "

        #create_table_sql = create_table_sql.rstrip(', ') + ")"

        # Execute the create or replace table SQL
        #self.cursor.execute(create_table_sql)

        # Use Pandas to upload DataFrame data to Snowflake
        #table_data.to_sql(table_name, self.connection, schema=self.snowflake_schema, index=False, if_exists='replace', method='multi')

        # Commit the changes
        #self.connection.commit()

        #insert_query = f"INSERT INTO {self.snowflake_database}.{self.snowflake_schema}.{table_name} VALUES (?, ?, ?, ?, ?, ?)"
        
        connection_parameters = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "role": os.getenv("SNOWFLAKE_ROLE"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA")
        }
        
        session = Session.builder.configs(connection_parameters).create()
        
        table_data['date'] = pd.to_datetime(table_data['date'])
        
        table_data.columns = table_data.columns.str.upper()

        session.write_pandas(
            df = table_data, 
            table_name = table_name.upper(), 
            auto_create_table=True,
            overwrite=True, 
        )

        # Execute the query
        #self.cursor.executemany(insert_query, table_data)
        
        # Commit the changes
        self.connection.commit()

    def close_connection(self):
        # Close the cursor and connection when done
        self.cursor.close()
        self.connection.close()
