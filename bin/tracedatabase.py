#!/usr/bin/python
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
        self.__trace_name = None
        self.__trace = None

        if trace_name.endswith('.gz'):
            with gzip.open(trace_name, 'rb') as trace_gz:
                self.__trace_name = os.path.splitext(trace_name)[0]
                self.__trace = trace_gz.readlines()
        else:
            self.__trace_name = trace_name
            self.__trace = open(trace_name, "r")

        self.__instructions = Instructions()
        self.__memory_access = MemoryAccess()
        self.__cycle_stats = CycleStatistics()

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

    def __parse_trace(self):
        """ Parse trace and save info to internal tables """
        # Start from cycle 0
        cycle = 0
        for line in self.__trace:
            if 'clk' in line:
                # Find which cycle and inc cycle counter
                cycle = int(re.search(r'(\d+)', line).group(1))
            self.__parse_inst(cycle, line)
            self.__parse_mem(cycle, line)

    def __write_database(self):
        """ Write to database """
        self.__cycle_stats.write_db(self.__get_database_name())
        self.__instructions.write_db(self.__get_database_name())
        self.__memory_access.write_db(self.__get_database_name())

    def run(self):
        """ Run parser and save to database """
        self.__parse_trace()
        self.__write_database()
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
