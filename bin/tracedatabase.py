#!/usr/bin/env python
""" This module contains helper functions to build database """

import gzip
import os
import sqlite3
import re
from traceinfo import Instructions
from traceinfo import MemoryAccess
from traceinfo import CycleStatistics


class DatabaseBuilder(object):
    """ Database builder for trace """

    def __init__(self, trace_name):
        self.__trace_name = os.path.splitext(trace_name)[0]
        self.__trace = None

        self.__cycle = 0
        self.__instructions = Instructions(self.__get_database_name())
        self.__memory_access = MemoryAccess(self.__get_database_name())
        self.__cycle_stats = CycleStatistics(self.__get_database_name())

        if trace_name.endswith('.gz'):
            with gzip.open(trace_name, 'rb') as trace_gz:
                for line in trace_gz:
                    self.__parse_trace(line)
        else:
            self.__trace_name = trace_name
            self.__trace = open(trace_name, "r")

    def __get_name(self, suffix):
        return self.__trace_name + suffix

    def __get_database_name(self):
        return self.__get_name('.db')

    def __parse_inst(self, cycle, line):
        """ Parse instruction info """
        if 'si.' in line:
            stage, cu_id = self.__instructions.parse(cycle, line)
            self.__cycle_stats.update(cycle, stage, cu_id)

    def __parse_mem(self, cycle, line):
        """ Parse memory info """
        if 'mem.' in line:
            self.__memory_access.parse(cycle, line)

    def __parse_trace(self, line):
        """ Parse trace and save info to internal tables """
        if 'clk' in line:
            self.__cycle = int(re.search(r'(\d+)', line).group(1))
        self.__parse_inst(self.__cycle, line)
        self.__parse_mem(self.__cycle, line)

    def run(self):
        """ Run parser and save to database """
        if os.path.isfile(self.__trace_name + ".db"):
            return sqlite3.connect(self.__get_database_name())


def load_database(trace_name):
    """ Load database """
    trace_db_name = os.path.splitext(trace_name)[0] + '.db'
    if os.path.isfile(trace_db_name):
        return sqlite3.connect(trace_db_name)
    else:
        db_builder = DatabaseBuilder(trace_name)
        return db_builder.run()
