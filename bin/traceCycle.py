#!/usr/bin/python
""" Trace Cycle visualizer for Multi2Sim """

import argparse
import pandas as pd
import numpy as np
from bokeh.charts import Histogram
from bokeh.plotting import figure, show, output_file
from bokeh.io import gridplot

import tracemisc as tm
import tracedatabase as td

FIGURE_WIDTH = 1100
FIGURE_HEIGHT = 450


class TraceCycleFigures(object):
    """TraceCycleFigures contains figures related to cycle tables """

    def __init__(self, trace_file):
        self.__trace_file = trace_file

        # Load database
        self.__database = td.load_database(self.__trace_file)

    def __build_database(self):
        self.__database = td.load_database(self.__trace_file)

    def get_column(self, table, column):
        """ Get a column from database """
        if self.__database is None:
            self.__build_database()

        cursor = self.__database.cursor()
        sql_query = 'SELECT ' + column + ' FROM ' + table

        return cursor.execute(sql_query)

    def get_column_with_func_cond(self,
                                  table, column,
                                  func_name, conditions=''):
        """ Get a column from database, apply with function """
        if self.__database is None:
            self.__build_database()

        cursor = self.__database.cursor()
        sql_query = 'SELECT ' + func_name
        sql_query += '(' + column + ') FROM ' + table + ' '
        sql_query += conditions
        return cursor.execute(sql_query).fetchone()[0]

    def get_max(self, table, column, conditions=''):
        """ Get the maximum of a column from database """
        return int(self.get_column_with_func_cond(table, column,
                                                  'MAX', conditions))

    def get_sum(self, table, column, conditions=''):
        """ Get the sum of a column from database """
        return int(self.get_column_with_func_cond(table, column,
                                                  'SUM', conditions))

    def get_count(self, table, column, conditions=''):
        """ Get the count of a column from database """
        return int(self.get_column_with_func_cond(table, column,
                                                  'COUNT', conditions))

    def get_column_list(self, table):
        """Get all columns as a list"""
        cursor = self.__database.cursor()
        sql_query = "PRAGMA table_info(" + table + ")"
        column_list = []
        metadata = cursor.execute(sql_query)
        for item in metadata:
            if item[1] != 'cycle':
                column_list.append(item[1])
        return sorted(column_list)

    def get_table_list(self):
        """Get all tables as a list"""
        cursor = self.__database.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = []
        for item in cursor.fetchall():
            table_list.append(item[0])
        return sorted(table_list)

    def plot_t_x_y(self, width, height,
                   table, x_column, y_column,
                   x_max=None, y_max=None):
        """ Plot a column from a table """
        plot_color = tm.get_random_color()

        # Get data from database
        sql_query = 'SELECT ' + x_column + ',' + y_column + \
            ' FROM ' + table
        dataframe = pd.read_sql_query(sql_query, self.__database)

        # Range
        if x_max is None:
            x_max = int(self.get_max(table, x_column))

        if y_max is None:
            y_max = int(self.get_max(table, y_column))

        # Plot
        plot_title = table + ' : ' + \
            str(self.get_max(table, x_column)) + ' / ' + y_column

        plot = figure(webgl=True,
                      width=width,
                      height=height,
                      x_range=(0, x_max),
                      y_range=(0, y_max),
                      title=plot_title)
        plot.xaxis.axis_label = x_column
        plot.yaxis.axis_label = 'Count'

        plot.segment(x0=dataframe[x_column],
                     y0=dataframe[y_column],
                     x1=dataframe[x_column],
                     y1=0,
                     line_width=1,
                     legend=y_column,
                     color=plot_color)

        # Plot histogram on the right, ignore zeroes
        dataframe_column = dataframe[y_column]
        mean = np.round(dataframe_column.mean(), 2)
        median = dataframe_column.median()
        hist_title = y_column
        hist_title += ' / avg ' + str(mean)
        hist_title += ' / mid ' + str(median)
        plot_hist = Histogram(dataframe_column,
                              y_column,
                              bins=50,
                              height=height,
                              width=height,
                              color=plot_color,
                              title=hist_title)

        return (plot, plot_hist)

    def plot_t_x_multi(self, width, height,
                       table, x_column, y_column_list,
                       x_range=None, y_range=None):
        """ Plot multiple columns, return a grid of figures """
        figures_vertical = []

        for y_column in sorted(y_column_list):
            plot, plot_hist = self.plot_t_x_y(
                width, height, table, x_column, y_column, x_range, y_range)
            figures_vertical.append([plot, plot_hist])
        return figures_vertical

    def plot_t_x_all(self, width, height,
                     table, x_column,
                     x_range=None, y_range=None):
        """ Plot all columns, return a grid of figures """

        column_list = self.get_column_list(table)
        return self.plot_t_x_multi(width, height, table, x_column,
                                   column_list, x_range, y_range)


class TraceCyclePlot(object):
    """Draw figures to file"""

    def __init__(self, trace, table, xaxis, yaxis):
        self.__trace = trace.split('.')[0]
        self.__figures = TraceCycleFigures(trace)

        # Table and Yaxis can be a list
        self.__table = None
        self.__xaxis = xaxis
        self.__yaxis = None

        # Draw function, default to draw selected columns in one table
        self.__draw_func = self.__draw_table_columns

        # Check tables
        trace_tables = self.__figures.get_table_list()
        valid_tables = []
        for item in table:
            if '*' not in item and item in trace_tables:
                valid_tables.append(item)
            else:
                for table in trace_tables:
                    if item[:-1] in table:
                        valid_tables.append(table)

        # Sanity check, at least 1 valid table
        if len(valid_tables) == 0:
            print 'No valid table found in trace'
            return

        # Check columns
        trace_columns = self.__figures.get_column_list(valid_tables[0])
        valid_columns = []
        for item in yaxis:
            if '*' not in item and item in trace_columns:
                valid_columns.append(item)
            else:
                for table in trace_columns:
                    if item[:-1] in table:
                        valid_columns.append(table)

        # Check and bind draw function
        if len(valid_tables) == 1:
            self.__table = valid_tables[0]
            self.__yaxis = valid_columns
            if 'all' in valid_columns:
                self.__draw_func = self.__draw_table_all_columns
            else:
                self.__draw_func = self.__draw_table_columns
        else:
            self.__table = valid_tables
            self.__yaxis = valid_columns
            self.__draw_func = self.__draw_compare_tables

    def __draw_table_columns(self):
        """ Show figures of multiple columns in a table """

        # Output file
        prefix = '_'.join([self.__trace, self.__table, self.__xaxis])
        if len(self.__yaxis) > 1:
            last = 'multi'
        else:
            last = self.__yaxis[0]
        output_name = '_'.join([prefix, last])
        output_file(output_name + '.html', title=output_name)

        # Get figures
        figures = self.__figures.plot_t_x_multi(FIGURE_WIDTH, FIGURE_HEIGHT,
                                                self.__table,
                                                self.__xaxis, self.__yaxis)
        plot = gridplot(figures)
        show(plot)

    def __draw_table_all_columns(self):
        """ Show figures of all columns in a table """

        # Output file
        output_name = '_'.join(
            [self.__trace, self.__table, self.__xaxis, 'all'])
        output_file(output_name + '.html', title=output_name)

        # Get figures
        figures = self.__figures.plot_t_x_all(FIGURE_WIDTH, FIGURE_HEIGHT,
                                              self.__table,
                                              self.__xaxis)
        plot = gridplot(figures)
        show(plot)

    def __draw_compare_tables(self):
        """ Compare multiple tables """

        # Sync X and Y range
        max_xaxis = 0
        for table in self.__table:
            max_xaxis = max(max_xaxis, self.__figures.get_max(table, 'cycle'))

        max_yaxis = {}
        for yaxis in self.__yaxis:
            max_val = 0
            for table in self.__table:
                max_val = max(max_val, self.__figures.get_max(table, yaxis))
            max_yaxis[yaxis] = max_val

        for yaxis in self.__yaxis:
            figures = []
            output_name = '_'.join(
                [self.__trace, 'multi', self.__xaxis, yaxis])
            output_file(output_name + '.html', title=output_name)

            for table in self.__table:
                xaxis = self.__xaxis
                plot, plot_hist = self.__figures.plot_t_x_y(FIGURE_WIDTH,
                                                            FIGURE_HEIGHT,
                                                            table,
                                                            xaxis,
                                                            yaxis,
                                                            max_xaxis,
                                                            max_yaxis[yaxis])
                figures.append([plot, plot_hist])

            plot = gridplot(figures)
            show(plot)

    def draw(self):
        """Call draw function object"""
        self.__draw_func()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Multi2Sim simulation trace cycle analyzer')
    parser.add_argument('trace', nargs=1,
                        help='Multi2Sim trace files')
    parser.add_argument("-t", "--table", nargs='+',
                        default="cycle_cu_0",
                        help='Choose a table')
    parser.add_argument("-y", "--yaxis", nargs='+',
                        default="f",
                        help='Choose columns in the table as y axis. '
                             'Use \'all\' to plot all columns. ')
    args = parser.parse_args()

    trace = args.trace[0]
    table = args.table
    xaxis = 'cycle'
    yaxis = args.yaxis

    # Traces
    cycle_view = TraceCyclePlot(trace, table, xaxis, yaxis)
    cycle_view.draw()


if __name__ == '__main__':
    main()
