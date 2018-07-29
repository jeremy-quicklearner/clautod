"""
Utilities for clautod database layer
"""

# IMPORTS ##############################################################################################################

# Standard Python modules
import sqlite3
from itertools import chain
from collections import OrderedDict

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.wildcard import WILDCARD
from clauto_common.util.log import Log
from clauto_common.util.config import ClautoConfig
from clauto_common.exceptions import DatabaseStateException

# Clautod Python modules


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautoDatabaseConnection:
    """
    A connection to the Clauto database (to be used in a WITH-statement)
    """
    def trace_callback(self, query):
        self.log.verbose("SQL Query: <%s>", query)

    def __init__(self, logging_enabled=True):
        self.db_filename = ClautoConfig()["db_dir"] + "/clauto.db"
        self.log = Log()
        self.logging_enabled = logging_enabled

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_filename)
        if self.logging_enabled:
            self.connection.set_trace_callback(self.trace_callback)
        return self

    def __exit__(self, a_type, value, traceback):
        self.connection.commit()
        self.connection.close()

    def select_all_records_by_table(self, table, min_records=None, max_records=None, num_fields_in_record=None):
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

        # Build the query
        query = 'SELECT * FROM %s;' % table

        # Execute the query
        result = self.connection.execute(query).fetchall()

        # Validate the results
        if min_records and len(result) < min_records:
            raise DatabaseStateException("All-Selection on table <%s> yielded too few records" % table)
        if max_records and len(result) > max_records:
            raise DatabaseStateException("All-Selection on table <%s> yielded too many records" % table)
        if num_fields_in_record and len(result) > 0 and len(result[0]) != num_fields_in_record:
            raise DatabaseStateException("All-Selection on table <%s> yielded malformed record(s)" % table)

        # Success
        return result

    def select_records_by_simple_condition_intersection(
            self,
            table,
            conditions,
            min_records=None,
            max_records=None,
            num_fields_in_record=None
    ):
        """
        Select the intersection of all records from a table that satisfy some conditions
        :param table: The table to select from
        :param conditions: A dict of the form {key1:value1,key2:value2,...}
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
            raise Exception("min_records > max_records in get_records_by_simple_value_conditions")

        # Remove all wildcards from conditions
        conditions = OrderedDict({key: value for key, value in conditions.items() if value is not WILDCARD}.items())

        # Build the query (with format specifiers in place of values)
        maybe_where = 'WHERE ' if len(conditions) else ''
        sql_conditions = ' AND '.join(['%s = ?' % key for key in conditions])

        # Execute the query
        result = self.connection.execute(
            ('SELECT * FROM %s %s' % (table, maybe_where)) + sql_conditions + ';',
            tuple(conditions[key] for key in conditions)
        ).fetchall()

        # Validate the results
        if min_records and len(result) < min_records:
            raise DatabaseStateException("Selection on table <%s> with conditions <%s> yielded too few records" %
                                         (table, conditions))
        if max_records and len(result) > max_records:
            raise DatabaseStateException("Selection on table <%s> with conditions <%s> yielded too many records" %
                                         (table, conditions))
        if num_fields_in_record and len(result) > 0 and len(result[0]) != num_fields_in_record:
            raise DatabaseStateException("Selection on table <%s> with conditions <%s> yielded malformed record(s)" %
                                         (table, conditions))

        # Success
        return result

    def select_records_by_simple_condition_union(
            self,
            table,
            conditions,
            min_records=None,
            max_records=None,
            num_fields_in_record=None
    ):
        """
        Select the union of all records from a table that satisfy some conditions
        :param table: The table to select from
        :param conditions: A dict of the form {key1:value1,key2:value2,...}
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
            raise Exception("min_records > max_records in get_records_by_simple_value_conditions")

        # Remove all wildcards from conditions
        conditions = OrderedDict({key: value for key, value in conditions.items() if value is not WILDCARD}.items())

        # Build the query (with format specifiers in place of values)
        maybe_where = 'WHERE ' if len(conditions) else ''
        sql_conditions = ' OR '.join(['%s = ?' % key for key in conditions])

        # Execute the query
        result = self.connection.execute(
            ('SELECT * FROM %s %s' % (table, maybe_where)) + sql_conditions + ';',
            tuple(conditions[key] for key in conditions)
        ).fetchall()

        # Validate the results
        if min_records and len(result) < min_records:
            raise DatabaseStateException("Selection on table <%s> with conditions <%s> yielded too few records" %
                                         (table, conditions))
        if max_records and len(result) > max_records:
            raise DatabaseStateException("Selection on table <%s> with conditions <%s> yielded too many records" %
                                         (table, conditions))
        if num_fields_in_record and len(result) > 0 and len(result[0]) != num_fields_in_record:
            raise DatabaseStateException("Selection on table <%s> with conditions <%s> yielded malformed record(s)" %
                                         (table, conditions))

        # Success
        return result

    def update_records_by_simple_condition_intersection(self, table, conditions, updates):
        """
        Update the intersection of all records from a table that satisfy some conditions
        :param table: The table to select from
        :param conditions: A dict of the form {key1:value1,key2:value2,...}
                            where each key/value pair must be found in a record
                            in the database in order for that record to be
                            included in the result
        :param updates: A dict of the form {key1:value1,key2:value2,...}
                        where the value of keyN in each selected record
                        will be updated to valueN
        """

        # If there are no updates, do nothing
        if len(updates) == 0:
            return

        # Remove all wildcards from conditions and updates
        conditions = OrderedDict({key: value for key, value in conditions.items() if value is not WILDCARD}.items())
        updates = OrderedDict({key: value for key, value in updates.items() if value is not WILDCARD}.items())

        # Build the query (with format specifiers in place of values)
        sql_updates = ', '.join(['%s = ?' % key for key in updates])
        maybe_where = 'WHERE ' if len(conditions) else ''
        sql_conditions = ' AND '.join(['%s = ?' % key for key in conditions])

        # Execute the query
        result = self.connection.execute(
            'UPDATE %s SET %s %s %s;' % (table, sql_updates, maybe_where, sql_conditions),
            tuple(chain(updates.values(), conditions.values()))
        ).fetchall()

        # Success
        return result

    def update_records_by_simple_condition_union(self, table, conditions, updates):
        """
        Update the union of all records from a table that satisfy some conditions
        :param table: The table to select from
        :param conditions: A dict of the form {key1:value1,key2:value2,...}
                            where each key/value pair must be found in a record
                            in the database in order for that record to be
                            included in the result
        :param updates: A dict of the form {key1:value1,key2:value2,...}
                        where the value of keyN in each selected record
                        will be updated to valueN
        """

        # If there are no updates, do nothing
        if len(updates) == 0:
            return

        # Remove all wildcards from conditions and updates
        conditions = OrderedDict({key: value for key, value in conditions.items() if value is not WILDCARD}.items())
        updates = OrderedDict({key: value for key, value in updates.items() if value is not WILDCARD}.items())

        # Build the query (with format specifiers in place of values)
        sql_updates = ', '.join(['%s = ?' % key for key in updates])
        maybe_where = 'WHERE ' if len(conditions) else ''
        sql_conditions = ' OR '.join(['%s = ?' % key for key in conditions])

        # Execute the query
        result = self.connection.execute(
            'UPDATE %s SET %s %s %s;' % (table, sql_updates, maybe_where, sql_conditions),
            tuple(chain(updates.values(), conditions.values()))
        ).fetchall()

        # Success
        return result

    def select_records_by_field(
            self,
            table,
            field,
            value,
            min_records=None,
            max_records=None,
            num_fields_in_record=None
    ):
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
        return self.select_records_by_simple_condition_intersection(
            table,
            {field: value},
            min_records,
            max_records,
            num_fields_in_record
        )

    def update_records_by_field(self, table, field, value, updates):
        """
        Update all records from a table, filtered by a field
        :param table: The table to select from
        :param field: The name of the column to filter by
        :param value: The value to filter with
        :param updates: A dict of the form {key1:value1,key2:value2,...}
                        where the value of keyN in each selected record
                        will be updated to valueN
        """
        self.select_records_by_simple_condition_intersection(table, {field: value}, updates)

    def select_record_by_key(self, table, key_name, key, num_fields_in_record=None, must_exist=False):
        """
        Get a record from a table which is uniquely identified by a key
        :param table: The table containing the record
        :param key_name: The name of the column which is the primary key
        :param key: The primary key of the record being selected
        :param num_fields_in_record: The number of fields that the record should have
        :param must_exist: Flag indicating whether the record is required to exist
        :return: The record, or None if it isn't in the database
        """

        records = self.select_records_by_field(table, key_name, key, int(must_exist), 1, num_fields_in_record)
        if len(records) == 0:
            return None
        else:
            return records[0]
