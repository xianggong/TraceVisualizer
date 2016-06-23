#!/usr/bin/env python
""" Trace Instruction visualizer for Multi2Sim """

import argparse
import pandas as pd
import numpy as np
from bokeh.models import BoxAnnotation
from bokeh.charts import Histogram
from bokeh.plotting import figure, show, output_file
from bokeh.io import gridplot

import tracemisc as tm
import tracedatabase as td

try:
    from intervaltree import Interval, IntervalTree
except ImportError:
    print 'Module not found! Install with "pip install intervaltree"'

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

    def get_interval(self, dataframe_s, dataframe_e):
        intervals = []

        if len(dataframe_s) == 0 and len(dataframe_e) == 0:
            return 0, []

        interval_s = dataframe_s[0]
        interval_e = dataframe_e[0]
        intervals.append((interval_s, interval_e))
        for index, value in enumerate(dataframe_s):
            interval_s = value
            interval_e = dataframe_e[index]
            range_s, range_e = intervals[-1]
            if range_s <= interval_s < range_e:
                if interval_e > range_e:
                    range_e = interval_e
                    intervals[-1] = (range_s, range_e)
            elif interval_s > range_e:
                intervals.append((interval_s, interval_e))

        cycle_count = 0
        for interval in intervals:
            interval_s, interval_e = interval
            cycle_count += interval_e - interval_s

        return cycle_count, intervals

    def get_interval_cu_cond(self, cu_id, condition):
        sql_query = 'SELECT start, start + length FROM inst WHERE cu=' + \
            str(cu_id)
        sql_query += ' AND unit_action ' + condition
        sql_query += ' ORDER by inst_order'
        dataframe = pd.read_sql_query(sql_query, self.__database)

        dataframe_s = dataframe['start']
        dataframe_e = dataframe['start + length']

        # print cu_id, condition, len(dataframe_s), len(dataframe_e)
        return self.get_interval(dataframe_s, dataframe_e)

    def get_interval_cu(self, cu_id):
        # MEM LD
        mem_ld_cycle, mem_ld_interval = self.get_interval_cu_cond(
            cu_id, 'LIKE "%MEM LD%"')

        mem_ld_interval_tree = IntervalTree(
            Interval(*iv) for iv in mem_ld_interval)

        # MEM ST
        mem_st_cycle, mem_st_interval = self.get_interval_cu_cond(
            cu_id, 'LIKE "%MEM ST%"')

        mem_st_interval_tree = IntervalTree(
            Interval(*iv) for iv in mem_st_interval)

        # OTHER
        other_cycle, other_interval = self.get_interval_cu_cond(
            cu_id, 'NOT LIKE "%MEM LD%"')

        other_interval_tree = IntervalTree(
            Interval(*iv) for iv in other_interval)

        cycle = self.get_max('inst', 'start + length',
                             ' WHERE cu=' + str(cu_id))
        # print cycle, mem_cycle, other_cycle

        info = {}
        info['mem_ld'] = mem_ld_interval_tree
        info['mem_st'] = mem_st_interval_tree
        info['other'] = other_interval_tree
        info['cycle_all'] = cycle
        info['cycle_mem_ld'] = mem_ld_cycle
        info['cycle_mem_st'] = mem_st_cycle
        info['cycle_other'] = other_cycle

        return info

    def get_interval_cu_all(self):
        sql_query = 'SELECT DISTINCT cu FROM inst'
        cu_id = pd.read_sql_query(sql_query, self.__database)

        for cu_id in sorted(cu_id['cu']):
            self.get_interval_cu(cu_id)

    def get_interval_boxannotation(self, cu_id):
        info = self.get_interval_cu(cu_id)

        mem_ld_interval_tree = info['mem_ld']
        mem_st_interval_tree = info['mem_st']
        other_interval_tree = info['other']

        annotation_box_list = []
        for interval in mem_ld_interval_tree:
            start = interval.begin
            end = interval.end
            box = BoxAnnotation(left=start, right=end,
                                fill_alpha=0.1, fill_color='red')
            annotation_box_list.append(box)

        for interval in mem_st_interval_tree:
            start = interval.begin
            end = interval.end
            box = BoxAnnotation(left=start, right=end,
                                fill_alpha=0.1, fill_color='blue')
            annotation_box_list.append(box)

        for interval in other_interval_tree:
            start = interval.begin
            end = interval.end
            box = BoxAnnotation(left=start, right=end,
                                fill_alpha=0.1, fill_color='green')
            annotation_box_list.append(box)

        return (annotation_box_list, info)

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

        # Get box annotation and cycle info
        boxannotations, info = self.get_interval_boxannotation(cu_id)
        cycle_all = info['cycle_all']
        cycle_mem_ld = info['cycle_mem_ld']
        cycle_mem_st = info['cycle_mem_st']
        cycle_other = info['cycle_other']

        # Title
        title = 'cu-' + str(cu_id) + ': '
        title += str(cycle_mem_ld) + ' mem ld / '
        title += str(cycle_mem_st) + ' mem st / '
        title += str(cycle_other) + ' other / '
        title += str(cycle_all) + ' all'

        plot = figure(webgl=True,
                      width=width,
                      height=height,
                      x_range=(0, x_max),
                      y_range=(0, y_max),
                      title=title)

        y_axis = range(len(dataframe.index))

        plot.segment(x0=dataframe['start'],
                     y0=y_axis,
                     x1=dataframe['start'] + dataframe['length'],
                     y1=y_axis,
                     line_width=1,
                     color=dataframe['color'])

        # Add box annotation
        for box in boxannotations:
            plot.add_layout(box)

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
            sql_query = 'SELECT start,length,stall,color FROM inst'
            sql_query += ' WHERE cu=' + str(cu_id)
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
        description='Multi2Sim simulation trace instruction analyzer')
    parser.add_argument('trace', nargs=1,
                        help='Multi2Sim trace files')
    args = parser.parse_args()

    trace = args.trace[0]

    # Plot timeline
    pipeline = TraceInstPlot(trace)
    pipeline.draw()


if __name__ == '__main__':
    main()
