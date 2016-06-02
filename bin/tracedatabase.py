#!/usr/bin/python
""" This module contains helper functions to build database """

import gzip
import os
import sqlite3
import re
import traceparser as tp
from traceinfo import Instructions
from traceinfo import CycleStatistics

MEM_NAME = 0
MEM_ACCESS_TYPE = 1
MEM_ACCESS_STATE = 2
MEM_ACCESS_LOCATION = 3
MEM_START = 4
MEM_LENGTH = 5
MEM_ADDR = 6
MEM_L1_ID = 7
MEM_L1_MISS_COUNT = 8
MEM_L2_ID = 9
MEM_L2_MISS_COUNT = 10
MEM_L3_ID = 11
MEM_L3_MISS_COUNT = 12
MEM_MM_ID = 13
MEM_MM_MISS_COUNT = 14
MEM_LINE = 15
MEM_ACCESS_ID = 16


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

        self.__mem_view = {}

        self.__instructions = Instructions()
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

    def __parse_mem(self, cycle, line_num, line):
        """ Parse memory info """
        if 'mem.' in line:
            if 'mem.new_access ' in line:
                #  Update counters
                # self.__inc_count(STAT_MEM_NEW_ALL, cycle)
                # if 'load' in line:
                #     self.__inc_count(STAT_MEM_NEW_ALL_LOAD, cycle)
                # elif 'store' in line:
                #     self.__inc_count(STAT_MEM_NEW_ALL_STORE, cycle)
                # if 'LDS' in line:
                #     self.__inc_count(STAT_MEM_NEW_LDS, cycle)
                #     if 'load' in line:
                #         self.__inc_count(STAT_MEM_NEW_LDS_LOAD, cycle)
                #     elif 'store' in line:
                #         self.__inc_count(STAT_MEM_NEW_LDS_STORE, cycle)
                # else:
                #     self.__inc_count(STAT_MEM_NEW_MM, cycle)
                #     if 'load' in line:
                #         self.__inc_count(STAT_MEM_NEW_MM_LOAD, cycle)
                #     elif 'store' in line:
                #         self.__inc_count(STAT_MEM_NEW_MM_STORE, cycle)

                mem_access_name = tp.get_name(line)
                mem_access_addr = tp.get_addr(line)
                mem_access_type = tp.get_type(line)
                mem_access_state = tp.get_state(line)
                mem_access_location = tp.get_state_location(line)
                mem_access_id = tp.get_access_id(line)
                self.__mem_view[mem_access_name] = [mem_access_name,
                                                    mem_access_type,
                                                    mem_access_state,
                                                    mem_access_location,
                                                    cycle,
                                                    -1,
                                                    mem_access_addr,
                                                    -1, -1,
                                                    -1, -1,
                                                    -1, -1,
                                                    -1, -1,
                                                    line_num,
                                                    mem_access_id]
            # elif 'mem.access ' in line:
                # mem_access_name = tp.get_name(line)
                # mem_access_state = tp.get_state(line)

            elif 'mem.end_access ' in line:
                mem_access_name = tp.get_name(line)
                mem_access_start = self.__mem_view[
                    mem_access_name][MEM_START]
                mem_access_length = cycle - mem_access_start
                self.__mem_view[mem_access_name][
                    MEM_LENGTH] = mem_access_length

    def __parse_trace(self):
        """ Parse trace and save info to internal tables """
        # Start from cycle 0
        cycle = 0
        line_num = 0
        for line in self.__trace:
            line_num += 1
            if 'clk' in line:
                # Find which cycle and inc cycle counter
                cycle = int(re.search(r'(\d+)', line).group(1))

            self.__parse_inst(cycle, line)
            self.__parse_mem(cycle, line_num, line)

    def __write_database_stat(self):
        self.__cycle_stats.write_db(self.__get_database_name())

    def __write_database_inst(self):
        self.__instructions.write_db(self.__get_database_name())

    def __write_database_mem(self):
        """ Write mem to database """
        database = sqlite3.connect(self.__get_database_name())
        cursor = database.cursor()

        # Create memory access table
        cursor.execute('''CREATE TABLE IF NOT EXISTS memory
            (name text, \
             access_type text, access_state text, access_location text, \
             cycle_start INTEGER, length INTEGER, addr text, \
             l1_id text, l1_miss_count INTEGER, \
             l2_id text, l2_miss_count INTEGER, \
             l3_id text, l3_miss_count INTEGER, \
             mm_id text, mm_miss_count INTEGER, \
             line INTEGER, mem_access_id INTEGER)''')

        # Add memory access data
        for key in self.__mem_view:
            name = self.__mem_view[key][MEM_NAME]
            access_type = self.__mem_view[key][MEM_ACCESS_TYPE]
            access_state = self.__mem_view[key][MEM_ACCESS_STATE]
            access_location = self.__mem_view[key][MEM_ACCESS_LOCATION]
            start = self.__mem_view[key][MEM_START]
            length = self.__mem_view[key][MEM_LENGTH]
            addr = self.__mem_view[key][MEM_ADDR]
            l1_id = self.__mem_view[key][MEM_L1_ID]
            l1_miss_count = self.__mem_view[key][MEM_L1_MISS_COUNT]
            l2_id = self.__mem_view[key][MEM_L2_ID]
            l2_miss_count = self.__mem_view[key][MEM_L2_MISS_COUNT]
            l3_id = self.__mem_view[key][MEM_L3_ID]
            l3_miss_count = self.__mem_view[key][MEM_L3_MISS_COUNT]
            mm_id = self.__mem_view[key][MEM_MM_ID]
            mm_miss_count = self.__mem_view[key][MEM_MM_MISS_COUNT]
            line = self.__mem_view[key][MEM_LINE]
            mem_access_id = self.__mem_view[key][MEM_ACCESS_ID]

            cursor.execute('INSERT INTO memory VALUES(?, ?, ?, ?, \
                                                 ?, ?, ?, \
                                                 ?, ?, \
                                                 ?, ?, \
                                                 ?, ?, \
                                                 ?, ?, \
                                                 ?, ?)',
                           (name, access_type, access_state, access_location,
                            start, length, addr,
                            l1_id, l1_miss_count,
                            l2_id, l2_miss_count,
                            l3_id, l3_miss_count,
                            mm_id, mm_miss_count,
                            line, mem_access_id))

        # Save (commit) the changes
        database.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        database.close()

    def __write_database(self):
        """ Write to database """
        self.__write_database_stat()
        self.__write_database_inst()
        self.__write_database_mem()

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
