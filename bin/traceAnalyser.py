#!/usr/bin/python
""" Trace analyzer for Multi2Sim """

import argparse
import collections
import pandas as pd
import numpy as np
from bokeh.charts import Histogram, Bar, Donut
from bokeh.plotting import figure, show, output_file
from bokeh.io import vplot, gridplot
from bokeh.charts import defaults
import os

import tracedatabase as td
import tracemisc as tm

SCREEN_WIDTH = 1560

defaults.width = int(SCREEN_WIDTH * 0.3)
defaults.height = defaults.width


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
                col_sched.append(self.get_file_name())
                col_location.append(key)
                col_value.append(mean)
                col_type.append('Mean')
                col_color.append(color)

                # Insert median
                col_sched.append(self.get_file_name())
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


class Traces(object):
    """ Traces """

    def __init__(self, trace_files):

        self.trace_files = trace_files
        self.traces = []
        self.plot_height = defaults.height
        self.plot_width = SCREEN_WIDTH - self.plot_height

        for trace_file in trace_files:
            trace = Trace(trace_file)
            self.traces.append(trace)

    def get_output_file_name(self):
        output_file_name = self.trace_files[0].split('_')
        for trace in self.trace_files:
            for index, item in enumerate(trace.split("_")):
                if output_file_name[index] != item:
                    output_file_name[index] = 'multi'
        return str('_').join(output_file_name).replace('.gz', '')

    def stat(self):
        """ Show all statistics """
        for trace in self.traces:
            trace.get_all_count()

    def plot_table_x_y(self, table_name, x_column_name, y_column_name):
        """ Plot traces """
        # Output to static HTML file
        output_file_name = self.get_output_file_name()
        output_file_name += "_" + y_column_name + "_" + x_column_name
        output_file(output_file_name + '.html', title=output_file_name)

        # List of figures
        figures = []

        # Set y axis range
        x_max = 0
        y_max = 0
        for trace in self.traces:
            x_max = max(trace.get_max(table_name, x_column_name), x_max)
            y_max = max(trace.get_max(table_name, y_column_name), y_max)
        x_max *= 1.01
        y_max *= 1.05

        # Plotting
        all_in_one = figure(webgl=True,
                            plot_width=self.plot_width,
                            plot_height=self.plot_height,
                            x_range=(0, x_max),
                            y_range=(0, y_max),
                            title='Combined view')
        all_in_one.xaxis.axis_label = x_column_name
        all_in_one.yaxis.axis_label = y_column_name

        # Statistic for comparison
        info_compare_list = []

        for trace in self.traces:

            # Get the data from database
            sql_query = 'SELECT ' + x_column_name + ',' + y_column_name + \
                ' FROM ' + table_name
            df = pd.read_sql_query(sql_query, trace.get_db())

            # Plot the main view
            plot_title = trace.get_file_name() + " : " + \
                str(trace.get_max("cycle", "cycle")) + " cycles"
            plot = figure(webgl=True,
                          plot_width=self.plot_width,
                          plot_height=self.plot_height,
                          x_range=all_in_one.x_range,
                          y_range=all_in_one.y_range,
                          title=plot_title)
            plot.xaxis.axis_label = x_column_name
            plot.yaxis.axis_label = y_column_name

            plot.segment(x0=df[x_column_name],
                         y0=df[y_column_name],
                         x1=df[x_column_name],
                         y1=0,
                         line_width=1,
                         legend=trace.get_file_name(),
                         color=trace.get_color())

            # Plot histogram on the right, ignore zeroes
            df_filter_zero = df[y_column_name].replace(0, np.nan)
            mean = np.round_(df_filter_zero.mean(), 2)
            median = df_filter_zero.median()
            hist_title = y_column_name
            hist_title += ' / avg ' + str(mean)
            hist_title += ' / mid ' + str(median)
            plot_hist = Histogram(df_filter_zero,
                                  y_column_name,
                                  bins=max(int(y_max / 10), 50),
                                  color=trace.get_color(),
                                  title=hist_title)

            all_in_one.segment(x0=df[x_column_name],
                               y0=df[y_column_name],
                               x1=df[x_column_name],
                               y1=0,
                               line_width=1,
                               legend=trace.get_file_name(),
                               color=trace.get_color())

            figures.append([plot, plot_hist])

            # Add statistic to comparison list
            info_compare_list.append(
                trace.get_stat_column_in_table(table_name))

        # Plot statistic comparison on the lower right
        info_df = pd.concat(info_compare_list)
        stats_compare = Bar(info_df,
                            values='data',
                            group='trace',
                            label='catagory',
                            color='color',
                            legend=False,
                            ylabel='Count',
                            title='Statistics')

        figures.append([all_in_one, stats_compare])

        # Plot all figures
        plots = gridplot(figures)
        show(plots)

    def plotPipeline(self, cu_id):
        # Output to static HTML file
        output_file_name = self.get_output_file_name()
        output_file_name += "_pipeline"
        if int(cu_id) != -1:
            output_file_name += '_cu_' + str(cu_id) + "_"
        else:
            output_file_name += '_all_cu_'
        output_file(output_file_name + '.html', title=output_file_name)

        # List of figures
        figures = []

        # Set y axis range
        x_max = 1
        y_max = 1
        for trace in self.traces:
            if int(cu_id) != -1:
                condition = 'WHERE cu=' + cu_id
                x_max = max(trace.get_max(
                    "inst", "cycle_start + length", condition), x_max)
                y_max = max(trace.get_count("inst", "line", condition), y_max)
            else:
                x_max = max(trace.get_max(
                    "inst", "cycle_start + length"), x_max)
                y_max = max(trace.get_count("inst", "line"), y_max)
        x_max *= 1.01
        y_max *= 1.05

        # Plotting
        all_in_one = figure(webgl=True,
                            plot_width=self.plot_width,
                            plot_height=self.plot_height,
                            x_range=(0, x_max),
                            y_range=(0, y_max),
                            title='Combined view')
        all_in_one.xaxis.axis_label = "cycle"
        all_in_one.yaxis.axis_label = "inst_id"

        for trace in self.traces:
            sql_query = 'SELECT cycle_start,length FROM inst'
            if int(cu_id) != -1:
                sql_query += ' WHERE cu=' + cu_id
            sql_query += ' ORDER by line'
            df = pd.read_sql_query(sql_query, trace.get_db())

            if int(cu_id) != -1:
                condition = 'WHERE cu=' + cu_id
                cycle_count = trace.get_max(
                    "inst", "cycle_start + length", condition)
                trace_title = trace.get_file_name() + ": " + str(cycle_count)
            else:
                trace_title = trace.get_file_name()

            plot = figure(webgl=True,
                          plot_width=self.plot_width,
                          plot_height=self.plot_height,
                          x_range=all_in_one.x_range,
                          y_range=all_in_one.y_range,
                          title=trace_title)
            plot.xaxis.axis_label = "cycle"
            plot.yaxis.axis_label = "inst_id"

            y_axis = range(len(df.index))

            plot.segment(x0=df["cycle_start"],
                         y0=y_axis,
                         x1=df["cycle_start"] + df["length"],
                         y1=y_axis,
                         line_width=1,
                         legend=trace.get_file_name(),
                         color=trace.get_color())
            plot.legend.location = "top_left"

            all_in_one.segment(x0=df["cycle_start"],
                               y0=y_axis,
                               x1=df["cycle_start"] + df["length"],
                               y1=y_axis,
                               line_width=1,
                               legend=trace.get_file_name(),
                               color=trace.get_color())
            all_in_one.legend.location = "top_left"

            figures.append(plot)

        figures.append(all_in_one)

        # Plot all figures
        p = vplot(*figures)
        show(p)

    def plot_memory_hist(self, mode='overview'):
        # Output to static HTML file
        output_file_name = self.get_output_file_name()
        output_file_name += "_memory_hist_" + mode
        output_file(output_file_name + '.html', title=output_file_name)

        # List of histogram figures
        figures = []
        data_df = []
        for trace in self.traces:
            mem_info = trace.get_memory_hists(mode)
            figures.append(mem_info['hist'])
            data_df.append(mem_info['info'])

        # Plot mean and median comparison bar charts
        bars = []
        for access_type_index in range(len(data_df[0])):
            data_df_list = []
            for index, item in enumerate(data_df):
                data_df_list.append(data_df[index][access_type_index])
            data_dfs = pd.concat(data_df_list)
            access_location = data_dfs['location'][0]
            fig_bar = Bar(data_dfs, values='value', group='sched',
                          color='color', legend='center', label='type',
                          title=access_location + ': Mean and Median',
                          ylabel='Cycles')
            bars.append(fig_bar)
        figures.append(bars)

        # Plot all figures
        plot = gridplot(figures)
        show(plot)

    def plotMemory(self, mode='stat'):
        # Output to static HTML file
        output_file_name = self.get_output_file_name()
        output_file_name += "_memory_" + mode
        output_file(output_file_name + '.html', title=output_file_name)

        # List of figures
        figures = []

        # Set y axis range
        x_max = 1
        y_max = 1
        for trace in self.traces:
            if mode == 'pipe':
                x_max = max(trace.get_max(
                    "memory", "cycle_start + length"), x_max)
                y_max = max(trace.get_count("memory", "mem_access_id"), y_max)
            elif mode == 'stat':
                x_max = max(trace.get_count("memory", "mem_access_id"), x_max)
                y_max = max(trace.get_max("memory", "length"), y_max)
        x_max *= 1.01
        y_max *= 1.05

        # Plotting
        all_in_one = figure(webgl=True,
                            plot_width=SCREEN_WIDTH,
                            plot_height=self.plot_height,
                            x_range=(0, x_max),
                            y_range=(0, y_max),
                            title='Combined view')
        all_in_one.xaxis.axis_label = "cycle"
        all_in_one.yaxis.axis_label = "mem access id"

        access_filter = ['access_type="nc_store"',
                         'access_type="load" and access_location!="LDS[0]"',
                         'access_type="store" and access_location!="LDS[0]"',
                         'access_type="load" and access_location="LDS[0]"',
                         'access_type="store" and access_location="LDS[0]"']

        accees_legend = ['M M: NC Store',
                         'M M: Load',
                         'M M, Store',
                         'LDS: Load',
                         'LDS: Store']

        for trace in self.traces:
            figure_row_list = []
            if mode != 'hist':
                plot = figure(webgl=True,
                              plot_width=SCREEN_WIDTH,
                              plot_height=self.plot_height,
                              x_range=all_in_one.x_range,
                              y_range=all_in_one.y_range,
                              title=trace.get_file_name())
                figure_row_list = [plot]

            for index in range(len(access_filter)):
                sql_query = 'SELECT cycle_start,length,mem_access_id \
                            FROM memory'
                sql_query += ' WHERE ' + access_filter[index]
                sql_query += ' ORDER by line'
                df = pd.read_sql_query(sql_query, trace.get_db())

                color = tm.get_random_color()
                if mode == 'stat':
                    plot.xaxis.axis_label = "mem access id"
                    plot.yaxis.axis_label = "cycle"
                    plot.segment(x0=df["mem_access_id"],
                                 y0=0,
                                 x1=df["mem_access_id"],
                                 y1=df["length"],
                                 line_width=1,
                                 legend=accees_legend[index],
                                 color=color)

                    all_in_one.segment(x0=df["mem_access_id"],
                                       y0=0,
                                       x1=df["mem_access_id"],
                                       y1=df["length"],
                                       line_width=1,
                                       legend=trace.get_file_name(),
                                       color=color)
                    all_in_one.legend.location = "top_left"

                elif mode == 'pipe':
                    plot.xaxis.axis_label = "cycle"
                    plot.yaxis.axis_label = "mem access id"
                    plot.segment(x0=df["cycle_start"],
                                 y0=df["mem_access_id"],
                                 x1=df["cycle_start"] + df["length"],
                                 y1=df["mem_access_id"],
                                 line_width=1,
                                 legend=accees_legend[index],
                                 color=color)

                    all_in_one.segment(x0=df["cycle_start"],
                                       y0=df["mem_access_id"],
                                       x1=df["cycle_start"] + df["length"],
                                       y1=df["mem_access_id"],
                                       line_width=1,
                                       legend=trace.get_file_name(),
                                       color=color)
                    all_in_one.legend.location = "top_left"

            figures.append(figure_row_list)

        figures.append([all_in_one])

        # Plot all figures
        p = gridplot(figures)
        show(p)


def main():
    # Arg parser
    parser = argparse.ArgumentParser(
        description='Multi2Sim simulation trace analyzer')
    parser.add_argument('traceFiles', nargs='+',
                        help='Multi2Sim trace files')

    parser.add_argument("-v", "--visual",
                        action="store_true",
                        help='Visualize statistics')
    parser.add_argument("-t", "--table", nargs=1,
                        default="cycle",
                        help='Choose table name')
    parser.add_argument("-x", "--xaxis", nargs=1,
                        default="cycle",
                        help='Choose x axis statistic name')
    parser.add_argument("-y", "--yaxis", nargs=1,
                        default="stall",
                        help='Choose y axis statistic name')

    parser.add_argument("-cu", "--cuid", nargs=1,
                        default=-1,
                        help='Filter on cumpute unit')
    parser.add_argument("-s", "--stat",
                        action="store_true",
                        help='Show statistics')
    parser.add_argument("-p", "--pipeline",
                        action="store_true",
                        help='Visualize pipeline')
    parser.add_argument("-m", "--memory",
                        choices=['pipe', 'stat'],
                        help='Visualize memory')
    parser.add_argument("-mh", "--memoryhist",
                        choices=['overview', 'detailed'],
                        help='Visualize memory access in histogram')
    args = parser.parse_args()

    # Sort the files in human natural order
    args.traceFiles.sort(key=tm.natural_keys)

    # Traces
    traces = Traces(args.traceFiles)

    # Statistics
    if args.stat:
        traces.stat()

    if args.visual:
        traces.plot_table_x_y(args.table[0], args.xaxis[0], args.yaxis[0])

    if args.pipeline:
        traces.plotPipeline(args.cuid[0])

    if args.memory:
        traces.plotMemory(args.memory)

    if args.memoryhist:
        traces.plot_memory_hist(args.memoryhist)

if __name__ == '__main__':
    main()
