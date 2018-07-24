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

    def get_all_records_by_table(self, table, min_records=None, max_records=None, num_fields_in_record=None):
        """
        Select all records from a table, filtered by a key
        :param table: The table to select from
        :param min_records: The minimum number of records that may be selected
        :param max_records: The maximum number of records that may be selected
        :param num_fields_in_record: The number of fields that should be in each record
        :return: An array of the records selected
        """

        # Sanity check
        if min_records and max_records and min_records > max_records:
            raise Exception("min_records > max_records in get_records_by_key")

        # Execute the query
        result = self.connection.execute(
            'SELECT * from %s;' % table
        ).fetchall()

        # Validate the results
        if min_records and len(result) < min_records:
            raise DatabaseStateException("All-Selection on table <%s> yielded too few records" % table)
        if max_records and len(result) > max_records:
            raise DatabaseStateException("All-Selection on table <%s> yielded too many records" % table)
        if num_fields_in_record and len(result) > 0 and len(result[0]) != num_fields_in_record:
            raise DatabaseStateException("All-Selection on table <%s> yielded malformed record(s)" % table)

        # Success
        return result

    def get_records_by_simple_constraint_intersection(
            self,
            table,
            constraints,
            min_records=None,
            max_records=None,
            num_fields_in_record=None
    ):
        """
        Select the intersection of all records from a table that satisfy some constraints
        :param table: The table to select from
        :param constraints: A dict of the form {key1:value1,key2:value2,...}
                            where each key/value pair must be found in a record
                            in the database in order for that record to be
                            included in the result
        :param min_records: The minimum number of records that may be selected
        :param max_records: The maximum number of records that may be selected
        :param num_fields_in_record: The number of fields that should be in each record
        :return: An array of the records selected
        """

        # Sanity check
        if min_records and max_records and min_records > max_records:
            raise Exception("min_records > max_records in get_records_by_simple_value_constraints")

        # Build the query (with format specifiers in place of values)
        maybe_where = 'WHERE ' if len(constraints) else ''
        sql_constraints = ' AND '.join(['%s = ?' % key for key in constraints.keys()])
        query = ('SELECT * FROM %s %s' % (table, maybe_where)) + sql_constraints + ';'

        # Execute the query
        result = self.connection.execute(
            query, tuple(constraints[key] for key in constraints.keys())
        ).fetchall()

        # Validate the results
        if min_records and len(result) < min_records:
            raise DatabaseStateException("Selection on table <%s> with constraints <%s> yielded too few records" %
                                         (table, constraints))
        if max_records and len(result) > max_records:
            raise DatabaseStateException("Selection on table <%s> with constraints <%s> yielded too many records" %
                                         (table, constraints))
        if num_fields_in_record and len(result) > 0 and len(result[0]) != num_fields_in_record:
            raise DatabaseStateException("Selection on table <%s> with constraints <%s> yielded malformed record(s)" %
                                         (table, constraints))

        # Success
        return result

    def get_records_by_simple_constraint_union(
            self,
            table,
            constraints,
            min_records=None,
            max_records=None,
            num_fields_in_record=None
    ):
        """
        Select the union of all records from a table that satisfy some constraints
        :param table: The table to select from
        :param constraints: A dict of the form {key1:value1,key2:value2,...}
                            where each key/value pair must be found in a record
                            in the database in order for that record to be
                            included in the result
        :param min_records: The minimum number of records that may be selected
        :param max_records: The maximum number of records that may be selected
        :param num_fields_in_record: The number of fields that should be in each record
        :return: An array of the records selected
        """

        # Sanity check
        if min_records and max_records and min_records > max_records:
            raise Exception("min_records > max_records in get_records_by_simple_value_constraints")

        # Build the query (with format specifiers in place of values)
        maybe_where = 'WHERE ' if len(constraints) else ''
        sql_constraints = ' OR '.join(['%s = ?' % key for key in constraints.keys()])
        query = ('SELECT * FROM %s %s' % (table, maybe_where)) + sql_constraints + ';'

        # Execute the query
        result = self.connection.execute(
            query, tuple(constraints[key] for key in constraints.keys())
        ).fetchall()

        # Validate the results
        if min_records and len(result) < min_records:
            raise DatabaseStateException("Selection on table <%s> with constraints <%s> yielded too few records" %
                                         (table, constraints))
        if max_records and len(result) > max_records:
            raise DatabaseStateException("Selection on table <%s> with constraints <%s> yielded too many records" %
                                         (table, constraints))
        if num_fields_in_record and len(result) > 0 and len(result[0]) != num_fields_in_record:
            raise DatabaseStateException("Selection on table <%s> with constraints <%s> yielded malformed record(s)" %
                                         (table, constraints))

        # Success
        return result

    def get_records_by_field(self, table, field, value, min_records=None, max_records=None, num_fields_in_record=None):
        """
        Select all records from a table, filtered by a field
        :param table: The table to select from
        :param field: The name of the column to filter by
        :param value: The value to filter with
        :param min_records: The minimum number of records that may be selected
        :param max_records: The maximum number of records that may be selected
        :param num_fields_in_record: The number of fields that should be in each record
        :return: An array of the records selected
        """
        return self.get_records_by_simple_constraint_intersection(
            table,
            {field:value},
            min_records,
            max_records,
            num_fields_in_record
        )

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
