import logging

import pandas as pd

from src.assignment_builder import AssignmentSimulator, ClusteredAssignmentSimulator
from src.fact_source_builder import FactSourceBuilder

console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

logger = logging.getLogger(__name__)
logger.level = logging.INFO
logger.addHandler(console_handler)
logger.propagate = False

ASSSIGNMENT_BUILDERS = {
    'standard': AssignmentSimulator,
    'clustered': ClusteredAssignmentSimulator
}


class DataSimulator:
    def __init__(self, config):
        self.config = config

    def generate_assignments(self):
        assignment_builder = ASSSIGNMENT_BUILDERS[self.config['type']](**self.config['assignments'])
        self.assignments = assignment_builder.simulate()

    def _get_fact_entity(self):
        if self.config['assignments'].get('subentity_name'):
            return self.config['assignments']['subentity_name']
        return self.config['assignments']['entity_name']

    def simulate_facts(self):
        fact_entity = self._get_fact_entity()

        self.fact_source_tables = {}
        for fact_source_id, fact_source_info in self.config['fact_sources'].items():
            fact_source_builder = FactSourceBuilder(self.assignments,
                                                    fact_source_info, fact_entity)

            self.fact_source_tables[fact_source_id] = fact_source_builder.simulate()

    def simulate(self):

        logger.info('generating assignments')
        self.generate_assignments()

        logger.info('simulating facts')
        self.simulate_facts()

    def log_data_summary(self):

        logger.info('assignments')
        logger.info(print(pd.DataFrame(self.assignments)))

        for fact_source_table_id, fact_source_data in self.fact_source_tables.items():
            logger.info(fact_source_table_id)
            logger.info(fact_source_data)

    def push_to_snowflake(self, snowflake_connection):
        logger.info('pushing assignments table')
        snowflake_connection.push_table(
            self.config['assignments_table_name'],
            pd.DataFrame(self.assignments)
        )

        for fact_source_table_id, fact_source_data in self.fact_source_tables.items():
            logger.info('pushing ' + fact_source_table_id + ' table')
            snowflake_connection.push_table(
                fact_source_table_id,
                fact_source_data
            )
