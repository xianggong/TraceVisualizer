#!/usr/bin/python
""" Multi2Sim trace object """

import collections
import os
import numpy as np
import pandas as pd
from bokeh.charts import Histogram, Donut

import tracedatabase as td
import tracemisc as tm


class Trace(object):
    """ Trace of Multi2Sim """

    def __init__(self, file_name):

        # Trace information
        self.__file_name = file_name
        self.__color = tm.get_random_color()

        # Load database
        self.__database = td.load_database(self.__file_name)

    def __build_database(self):
        self.__database = td.load_database(self.__file_name)

    def get_file_name(self):
        """ Get file name """
        try:
            return os.path.splitext(self.__file_name)[0]
        except IndexError:
            return 'na'

    def get_name_gpu_config(self):
        """ Get name of GPU configuration from file name """
        try:
            return self.__file_name.split('_')[0]
        except IndexError:
            return 'na'

    def get_name_kernel(self):
        """ Get name of kernel from file name """
        try:
            return self.__file_name.split('_')[1]
        except IndexError:
            return 'na'

    def get_name_instruction_scheduler(self):
        """ Get name of instruction scheduler from file name """
        try:
            return self.__file_name.split('_')[3]
        except IndexError:
            return 'na'

    def get_work_size(self):
        """ Get workload length from file name """
        return str(self.__file_name.split('_')[4])

    def get_color(self):
        """ Get color assigned to trace """
        return self.__color

    def get_db(self):
        """ Get database """
        return self.__database

    def get_column(self, table_name, column_name):
        """ Get a column from database """
        if self.__database is None:
            self.__build_database()

        cursor = self.__database.cursor()
        sql_query = 'SELECT ' + column_name + ' FROM ' + table_name

        return cursor.execute(sql_query)

    def get_column_with_func_cond(self,
                                  table_name, column_name,
                                  func_name, conditions=''):
        """ Get a column from database, apply with function """
        if self.__database is None:
            self.__build_database()

        cursor = self.__database.cursor()
        sql_query = 'SELECT ' + func_name
        sql_query += '(' + column_name + ') FROM ' + table_name + ' '
        sql_query += conditions
        return cursor.execute(sql_query).fetchone()[0]

    def get_max(self, table_name, column_name, conditions=''):
        """ Get the maximum of a column from database """
        return int(self.get_column_with_func_cond(table_name, column_name,
                                                  'MAX', conditions))

    def get_sum(self, table_name, column_name, conditions=''):
        """ Get the sum of a column from database """
        return int(self.get_column_with_func_cond(table_name, column_name,
                                                  'SUM', conditions))

    def get_count(self, table_name, column_name, conditions=''):
        """ Get the count of a column from database """
        return int(self.get_column_with_func_cond(table_name, column_name,
                                                  'COUNT', conditions))

    def print_table_columns_with_func(self, table_name, func_name):
        """ Print table columns information """
        cursor = self.__database.cursor()
        cursor.execute('SELECT * from ' + table_name)

        field_names = [i[0] for i in cursor.description]
        print 'Table: ' + table_name
        for column in field_names:
            output = '  ' + column.ljust(16)
            output += '\t' + str(self.get_column_with_func_cond(table_name,
                                                                column,
                                                                func_name))
            print output

    def get_all_count(self):
        """ Get all the count """
        print "Cycle 0 to " + str(self.get_max("cycle", "cycle"))
        self.print_table_columns_with_func('cycle', 'SUM')

    def __get_valid_column_action(self, table_name):
        """ Get columes with meaningful statistic and the function to apply """
        stats = {}

        if table_name == 'cycle':
            stats['cycle'] = 'MAX'
            stats['stall'] = 'SUM'
            stats['fetch'] = 'SUM'
            stats['issue'] = 'SUM'
            stats['branch'] = 'SUM'
            stats['mem'] = 'SUM'
            stats['lds'] = 'SUM'
            stats['scalar'] = 'SUM'
            stats['simd'] = 'SUM'
            stats['mem_new_all'] = 'SUM'
            stats['mem_new_all_load'] = 'SUM'
            stats['mem_new_all_store'] = 'SUM'
            stats['mem_new_lds'] = 'SUM'
            stats['mem_new_lds_load'] = 'SUM'
            stats['mem_new_lds_store'] = 'SUM'
            stats['mem_new_mm'] = 'SUM'
            stats['mem_new_mm_load'] = 'SUM'
            stats['mem_new_mm_store'] = 'SUM'
        elif table_name == 'inst':
            stats['stall'] = 'SUM'
            stats['fetch'] = 'SUM'
            stats['issue'] = 'SUM'
            stats['active'] = 'SUM'
        elif table_name == 'memory':
            stats['length'] = 'MAX'

        return stats

    def get_stat_column_in_table(self, table_name):
        """ Get statistic of each column in a table, return as a dataframe """

        col_field_cat = []
        col_field_data = []
        col_field_color = []
        col_field_index = []

        actions = self.__get_valid_column_action(table_name)
        for key, value in actions.iteritems():
            col_field_cat.append(key)
            col_field_data.append(
                self.get_column_with_func_cond(table_name, key, value))
            col_field_color.append(self.get_color())
            col_field_index.append(self.get_file_name())

        data_sum = {'catagory': col_field_cat,
                    'data': col_field_data,
                    'color': col_field_color,
                    'trace': col_field_index}
        data_sum_df = pd.DataFrame(data_sum, index=col_field_index)

        return data_sum_df

    def __get_memory_access_detailed(self):
        """ Get all memory access types """
        sql_query = 'SELECT DISTINCT access_location, access_type FROM memory '
        sql_query += 'ORDER by  access_location, access_type'
        dataframe = pd.read_sql_query(sql_query, self.get_db())
        return dataframe

    def __get_memory_access_types(self, mode='overview'):
        """ Get overview of memory access types """
        access = collections.OrderedDict()

        if mode == 'overview':
            access['M M: Load'] = 'access_type="load" \
                                   and access_location!="LDS[0]"'
            access['M M: Store'] = 'access_type="store" \
                                    and access_location!="LDS[0]"'
            access['M M: NC Store'] = 'access_type="nc_store"'
            access['LDS: Load'] = 'access_type="load" \
                                   and access_location="LDS[0]"'
            access['LDS: Store'] = 'access_type="store" \
                                   and access_location="LDS[0]"'
        elif mode == 'detailed':
            access_combinations = self.__get_memory_access_detailed()
            for index, row in access_combinations.iterrows():
                loc = row['access_location']
                aty = row['access_type']
                sql_query = 'access_location="' + loc
                sql_query += '" and access_type="' + aty + '"'
                access[loc + " " + aty] = sql_query

        return access

    def get_memory_hists(self, mode='overview'):
        """ Plot memory histogram in a row """
        access = self.__get_memory_access_types(mode)

        hists = []
        data_dfs = []

        col_cycle = []
        col_index = []

        for key, value in access.iteritems():
            sql_query = 'SELECT length FROM memory'
            sql_query += ' WHERE ' + value
            sql_query += ' ORDER by line'
            dataframe = pd.read_sql_query(sql_query, self.get_db())

            color = tm.get_random_color()

            col_sched = []
            col_location = []
            col_value = []
            col_type = []
            col_color = []

            try:
                # Some statistics
                mean = np.round_(dataframe["length"].mean(), 2)
                median = dataframe["length"].median()
                sum_len = dataframe["length"].sum()
                col_cycle.append(sum_len)
                col_index.append(key)

                # Plot histogram
                hist_title = key
                hist_title += ' / avg ' + str(mean)
                hist_title += ' / mid ' + str(median)
                plot_hist = Histogram(dataframe["length"].replace(0, np.nan),
                                      'length',
                                      bins=50,
                                      color=color,
                                      xlabel='Latency of instruction in cycle',
                                      ylabel='Count',
                                      title=hist_title)
            except ValueError:
                continue

            # Ignore NaN
            if mean == mean and median == median:
                # Insert mean
                col_sched.append(self.get_name_instruction_scheduler())
                col_location.append(key)
                col_value.append(mean)
                col_type.append('Mean')
                col_color.append(color)

                # Insert median
                col_sched.append(self.get_name_instruction_scheduler())
                col_location.append(key)
                col_value.append(median)
                col_type.append('Median')
                col_color.append(color)

                data = {'sched': col_sched,
                        'location': col_location,
                        'value': col_value,
                        'type': col_type,
                        'color': col_color}
                data_df = pd.DataFrame(data, index=col_location)
                data_dfs.append(data_df)

            hists.append(plot_hist)

        # Plot break down of cycles
        data = {'cycle': col_cycle}
        cycle_df = pd.DataFrame(data, index=col_index)
        pie_cycle = Donut(cycle_df.replace(0, np.nan),
                          title='Break down: cycles')
        hists.append(pie_cycle)

        info = {'hist': hists,
                'info': data_dfs}
        return info
