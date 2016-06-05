#!/usr/bin/python
""" Trace Instruction visualizer for Multi2Sim """

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


class TraceInstFigures(object):
    """docstring for TraceInstFigures"""

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

    def plot_timeline_cu(self, width, height,
                         dataframe, cu_id,
                         x_max=None, y_max=None):
        """ Plot timeline """
        # Plot
        plot_color = tm.get_random_color()

        # Range
        condition = 'WHERE cu=' + str(cu_id)
        if x_max is None:
            x_max = int(self.get_max("inst", "start + length", condition))

        if y_max is None:
            y_max = int(self.get_count("inst", "uid", condition))

        plot = figure(webgl=True,
                      width=width,
                      height=height,
                      x_range=(0, x_max),
                      y_range=(0, y_max),
                      title='cu-' + str(cu_id))

        y_axis = range(len(dataframe.index))

        plot.segment(x0=dataframe['start'],
                     y0=y_axis,
                     x1=dataframe['start'] + dataframe['length'],
                     y1=y_axis,
                     line_width=1,
                     color=plot_color)

        # Plot histogram on the right, ignore zeroes
        mean = np.round(dataframe['stall'].mean(), 2)
        median = dataframe['stall'].median()
        hist_title = 'stall'
        hist_title += ' / avg ' + str(mean)
        hist_title += ' / mid ' + str(median)
        plot_hist = Histogram(dataframe,
                              'stall',
                              bins=50,
                              height=height,
                              width=height,
                              color=plot_color,
                              title=hist_title)

        return (plot, plot_hist)

    def plot_timeline_all_cu(self):
        # Get unique cu
        sql_query = 'SELECT DISTINCT cu FROM inst'
        cu_id = pd.read_sql_query(sql_query, self.__database)

        figures_vertical = []

        x_max = self.get_max("inst", "start + length")
        for cu_id in sorted(cu_id['cu']):
            sql_query = 'SELECT start,length,stall FROM inst WHERE cu=' + \
                str(cu_id)
            sql_query += ' ORDER by inst_order'
            dataframe = pd.read_sql_query(sql_query, self.__database)
            plot, plot_hist = self.plot_timeline_cu(
                FIGURE_WIDTH, FIGURE_HEIGHT, dataframe, cu_id, x_max)
            figures_vertical.append([plot, plot_hist])

        return figures_vertical


class TraceInstPlot(object):
    """docstring for TraceInstPlot"""

    def __init__(self, trace):
        self.__trace = trace.split('.')[0]
        self.__figures = TraceInstFigures(trace)

    def draw(self):
        """ Draw pipeline """
        output_name = self.__trace + '_instruction_timeline'
        output_file(output_name + '.html', title=output_name)

        figures = self.__figures.plot_timeline_all_cu()

        plot = gridplot(figures)
        show(plot)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Multi2Sim simulation trace cycle analyzer')
    parser.add_argument('trace', nargs=1,
                        help='Multi2Sim trace files')
    args = parser.parse_args()

    trace = args.trace[0]

    # Plot timeline
    pipeline = TraceInstPlot(trace)
    pipeline.draw()


if __name__ == '__main__':
    main()
