"""
Utilities for clautod database layer
"""

# IMPORTS ##############################################################################################################

# Standard Python modules
import sqlite3

# Other Python modules

# Clauto Common Python modules
from clauto_common.util.config import ClautoConfig
from clauto_common.exceptions import DatabaseStateException

# Clautod Python modules


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautoDatabaseConnection:
    """
    A connection to the Clauto database (to be used in a WITH-statement)
    """

    def __init__(self):
        self.db_filename = ClautoConfig()["db_dir"] + "/clauto.db"

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_filename)
        return self

    def __exit__(self, a_type, value, traceback):
        self.connection.close()

    def get_records_by_key(self, table, key_name, key, min_records=None, max_records=None, num_fields_in_record=None):
        """
        Select all records from a table, filtered by a key
        :param table: The table to select from
        :param key_name: The name of the column to filter by
        :param key: The value to filter with
        :param min_records: The minimum number of records that may be selected
        :param max_records: The maximum number of records that may be selected
        :param num_fields_in_record: The number of fields that should be in each record
        :return: An array of the records selected
        """

        # Sanity check
        if min_records > max_records:
            raise Exception()

        # Execute the query
        result = self.connection.execute(
            'SELECT * from %s WHERE %s = ?;' % (table, key_name), (key,)
        ).fetchall()

        # Validate the results
        if min_records and len(result) < min_records:
            raise DatabaseStateException("Selection on table <%s> with key <%s> yielded too few records", table, key)
        if max_records and len(result) > max_records:
            raise DatabaseStateException("Selection on table <%s> with key <%s> yielded too many records", table, key)
        if num_fields_in_record and len(result) > 0 and len(result[0]) != num_fields_in_record:
            raise DatabaseStateException("Selection on table <%s> with key <%s> yielded malformed record(s)", table, key
                                         )

        # Success
        return result

    def get_record_by_key(self, table, key_name, key, num_fields_in_record=None, must_exist=False):
        """
        Get a record from a table which is uniquely identified by a key
        :param table: The table containing the record
        :param key_name: The name of the column which is the primary key
        :param key: The primary key of the record being selected
        :param num_fields_in_record: The number of fields that the record should have
        :param must_exist: Flag indicating whether the record is required to exist
        :return: The record, or None if it isn't in the database
        """

        records = self.get_records_by_key(table, key_name, key, int(must_exist), 1, num_fields_in_record)
        if len(records) == 0:
            return None
        else:
            return records[0]
