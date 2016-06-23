#!/usr/bin/env python
""" This module contains object describe a line in the trace """

import re
import sqlite3
import traceregex as tr
import traceISA as isa

DATA_THRESHOLD = 8192


class Instructions(object):
    """Instructions in trace"""

    def __init__(self, db_name):
        self.__instruction_count = 1

        self.__processing = {}
        self.__processed = {}

        self.__database = self.__create_db(db_name)

    def __del__(self):
        # Write remaining data to database
        if bool(self.__processed):
            self.__write_db(self.__processed)
        if bool(self.__processing):
            self.__write_db(self.__processing)

        # Close database
        self.__database.close()

    def __create_db(self, db_name):
        database = sqlite3.connect(db_name)
        cursor = database.cursor()

        # Create inst table
        sql_create_table = 'CREATE TABLE IF NOT EXISTS inst'
        columns = ('uid TEXT, id INTEGER, start INTEGER, length INTEGER, '
                   'stall INTEGER, fetch INTEGER, issue INTEGER, '
                   'active INTEGER, cu INTEGER, ib INTEGER, wf INTEGER, '
                   'wg INTEGER, uop_id INTEGER, scalar_vector TEXT, '
                   'unit_action TEXT, life_full TEXT, life_lite TEXT, '
                   'asm TEXT, inst_order INTEGER, color TEXT')
        query = sql_create_table + '(' + columns + ')'
        cursor.execute(query)

        # Save (commit) the changes
        database.commit()

        return database

    def __write_db(self, data_dict):
        database = self.__database
        cursor = database.cursor()

        # Insert data
        for key in data_dict:
            inst = data_dict[key]
            columns = ', '.join(inst.keys())
            placeholders = ':' + ', :'.join(inst.keys())
            placeholders = placeholders.replace('-', '_')  # - to _
            query = 'INSERT INTO inst (%s) VALUES (%s)' % (
                columns, placeholders)
            cursor.execute(query, inst)

        # Save (commit) the changes
        database.commit()

    def __get_inst_by_uid(self, uid):
        if uid in self.__processing:
            return self.__processing[uid]
        else:
            return None

    def __update_inst_exe(self, cycle, uid, line):
        inst = self.__get_inst_by_uid(uid)
        info = tr.parse_inst_exe(line).groupdict()
        inst['life_full'] += str(cycle) + str(info['stage']) + ', '

        return (info['stage'], info['cu'])

    def __update_inst_new(self, cycle, uid, line):
        self.__processing[uid] = {}
        inst = self.__get_inst_by_uid(uid)
        info = tr.parse_inst_new(line).groupdict()

        inst['uid'] = uid
        inst['inst_order'] = self.__instruction_count
        self.__instruction_count += 1
        inst['start'] = cycle
        inst['life_full'] = str(cycle) + str(info['stage']) + ', '
        for key, value in info.iteritems():
            if key != 'stage':
                self.__processing[uid][key] = value
        inst_info = isa.get_info(info['asm'])
        inst['scalar_vector'] = inst_info[1]
        inst['unit_action'] = inst_info[2]
        inst['color'] = inst_info[3]
        return (info['stage'], info['cu'])

    def __update_inst_end(self, cycle, uid, line):
        inst = self.__processing[uid]
        info = tr.parse_inst_end(line).groupdict()
        inst['length'] = int(cycle) - inst['start']
        inst['life_full'] += str(cycle) + 'end'

        # Get life lite
        inst_life = re.findall(r'(\d+)(\w+(-\w+)*)', inst['life_full'])
        inst_life_lite = []
        index = 0
        while index < len(inst_life) - 1:
            curr_index = index
            next_index = index + 1
            curr_stage = inst_life[curr_index][1]
            next_stage = inst_life[next_index][1]
            while curr_stage == next_stage:
                next_index += 1
                next_stage = inst_life[next_index][1]
            index = next_index
            cycle = int(inst_life[next_index][0]) - \
                int(inst_life[curr_index][0])
            inst_life_lite.append((str(cycle), curr_stage))

        count = {"fetch": 0, "stall": 0, "issue": 0, "active": 0}
        inst_life_string = ""
        for item in inst_life_lite:
            inst_life_string += item[0] + " " + item[1] + ", "
            if item[1] == "f":
                count['fetch'] += int(item[0])
            elif item[1].startswith("s_"):
                count['stall'] += int(item[0])
            elif item[1] == "i":
                count['issue'] += int(item[0])
            else:
                count['active'] += int(item[0])
        inst['life_lite'] = inst_life_string[:-2]
        for key, value in count.iteritems():
            self.__processing[uid][key] = value

        # Move to processed instructions
        self.__processed[uid] = self.__processing.pop(uid)

        # Flush to database periodically
        if len(self.__processed) >= DATA_THRESHOLD:
            self.__write_db(self.__processed)
            self.__processed.clear()

        return ('end', info['cu'])

    def parse(self, cycle, line):
        """Parse a line and return (stage, cu_id)"""
        uid = str(tr.get_inst_uid(line))

        # si.inst
        if tr.parse_inst_exe(line) is not None:
            return self.__update_inst_exe(cycle, uid, line)

        # si.new_inst
        elif tr.parse_inst_new(line) is not None:
            return self.__update_inst_new(cycle, uid, line)

        # si.end_inst
        elif tr.parse_inst_end(line) is not None:
            return self.__update_inst_end(cycle, uid, line)

        return (None, None)


class CycleStatistics(object):
    """CycleStatistics contains several CycleStatisticsCU objects"""

    def __init__(self, db_name):
        self.__db_name = db_name
        self.__cycle_stats = {}

    def update(self, cycle, stage, cu_id,):
        """Update"""
        if cu_id is None:
            return

        try:
            self.__cycle_stats[cu_id].update(cycle, stage)
        except KeyError:
            self.__cycle_stats[cu_id] = CycleStatisticsCU(
                cu_id, self.__db_name)
            self.__cycle_stats[cu_id].update(cycle, stage)


class CycleStatisticsCU(object):
    """CycleStatisticsCU contains stats of each cycle for each compute unit"""

    def __init__(self, cu_id, db_name):
        self.__cu_id = cu_id
        self.__cycle = 1

        self.__processing = {}
        self.__processed = {}
        self.__stages = {}
        self.__database = self.__create_db(db_name)

    def __del__(self):
        # Write remaining data to database
        if bool(self.__processed):
            self.__write_db(self.__processed)
        if bool(self.__processing):
            self.__write_db(self.__processing)

        # Close database
        self.__database.close()

    def __get_column_list(self, table):
        """Get all columns as a list"""
        cursor = self.__database.cursor()
        sql_query = "PRAGMA table_info(" + table + ")"
        column_list = []
        metadata = cursor.execute(sql_query)
        for item in metadata:
            if item[1] != 'cycle':
                column_list.append(item[1])
        return sorted(column_list)

    def __create_db(self, db_name):
        database = sqlite3.connect(db_name)
        cursor = database.cursor()

        # Create an empty table
        table_name = 'cycle_cu_' + str(self.__cu_id)
        query = 'CREATE TABLE IF NOT EXISTS ' + table_name + ' (cycle INTEGER)'
        cursor.execute(query)

        # Save (commit) the changes
        database.commit()

        return database

    def __write_db(self, data_dict):
        database = self.__database
        cursor = database.cursor()

        table_name = 'cycle_cu_' + str(self.__cu_id)

        # Check if column exists in table
        database_columns = sorted(self.__get_column_list(table_name))
        datadict_columns = sorted(self.__stages.keys())
        diff_columns = set(datadict_columns) - set(database_columns)

        # Add columns to database if necessary
        if diff_columns is not None:
            for column in sorted(list(diff_columns)):
                query = 'ALTER TABLE ' + table_name + ' ADD COLUMN ' + \
                    column.replace('-', '_') + ' INTEGER'
                cursor.execute(query)
            database.commit()

        # Insert data
        for key in data_dict:
            data = data_dict[key]
            columns = ', '.join(data.keys())
            placeholders = ':' + ', :'.join(data.keys())
            placeholders = placeholders.replace('-', '_')  # - to _
            query = 'INSERT INTO ' + table_name + ' (%s) VALUES (%s)' % (
                columns, placeholders)
            cursor.execute(query, data)

        # Save (commit) the changes
        database.commit()

    def update(self, cycle, stage):
        """ Update cycle statistics"""
        if stage is not None:
            stage = stage.replace('-', '_')
            self.__stages[stage] = 1

            # Update cycle info dictionary
            try:
                cycle_dict = self.__processing[cycle]
                try:
                    cycle_dict[stage] += 1
                except KeyError:
                    cycle_dict[stage] = 1
            except KeyError:
                self.__processing[cycle] = {}
                self.__processing[cycle]['cycle'] = cycle
                self.__processing[cycle][stage] = 1

            if cycle != self.__cycle:
                cycle_info = self.__processing.pop(self.__cycle)
                self.__processed[self.__cycle] = cycle_info
                self.__cycle = cycle

            if len(self.__processed) > DATA_THRESHOLD:
                self.__write_db(self.__processed)
                self.__processed.clear()


class MemoryAccess(object):
    """Memory access information"""

    def __init__(self, db_name):
        self.__processing = {}
        self.__processed = {}

        self.__database = self.__create_db(db_name)

    def __del__(self):
        # Write remaining data to database
        if bool(self.__processed):
            self.__write_db(self.__processed)
        if bool(self.__processing):
            self.__write_db(self.__processing)

        # Close database
        self.__database.close()

    def __create_db(self, db_name):
        database = sqlite3.connect(db_name)
        cursor = database.cursor()

        # Create inst table
        sql_create_table = 'CREATE TABLE IF NOT EXISTS mem_access'
        columns = ('uid INTEGER, module TEXT, type TEXT, address TEXT, '
                   'start INTEGER, length INTEGER, miss INTEGER, '
                   'life_full TEXT')
        columns = columns.replace('-', '_')  # - to _
        query = sql_create_table + '(' + columns + ')'
        cursor.execute(query)

        # Save (commit) the changes
        database.commit()

        return database

    def __write_db(self, data_dict):
        database = self.__database
        cursor = database.cursor()

        # Insert data
        for key in data_dict:
            mem_access = data_dict[key]
            columns = ', '.join(mem_access.keys())
            placeholders = ':' + ', :'.join(mem_access.keys())
            placeholders = placeholders.replace('-', '_')  # - to _
            query = 'INSERT INTO mem_access' + ' (%s) VALUES (%s)' % (
                columns, placeholders)
            cursor.execute(query, mem_access)

        # Save (commit) the changes
        database.commit()

    def __update_mem_new(self, cycle, uid, line):
        info = tr.parse_mem_new(line).groupdict()

        # Create an entry in mem access
        self.__processing[uid] = {}

        # Update memory access view
        mem_access = self.__processing[uid]
        mem_access['uid'] = uid
        mem_access['start'] = cycle
        mem_access['miss'] = 0
        mem_access['module'] = info['module']
        mem_access['type'] = info['type']
        mem_access['address'] = info['addr']
        mem_access['life_full'] = []
        mem_access_life = str(cycle) + ' ' + \
            info['module'] + ' ' + info['action']
        mem_access['life_full'].append(mem_access_life)

    def __update_mem_acc(self, cycle, uid, line):
        info = tr.parse_mem_acc(line).groupdict()

        # Update memory access view
        mem_access = self.__processing[uid]
        mem_access_life = str(cycle) + ' ' + \
            info['module'] + ' ' + info['action']
        if 'miss' in info['action']:
            mem_access['miss'] += 1
        mem_access['life_full'].append(mem_access_life)

    def __update_mem_end(self, cycle, uid):
        mem_access = self.__processing[uid]
        mem_access['length'] = cycle - int(mem_access['start'])
        mem_access['life_full'].append(str(cycle) + ' end')

        mem_access_life_full = ', '.join(mem_access['life_full'])
        mem_access['life_full'] = mem_access_life_full

        # Move to processed instructions
        self.__processed[uid] = self.__processing.pop(uid)

        # Flush to database periodically
        if len(self.__processed) >= DATA_THRESHOLD:
            self.__write_db(self.__processed)
            self.__processed.clear()

    def parse(self, cycle, line):
        """Parse a line """

        uid = tr.get_mem_uid(line)
        # mem.access
        if tr.parse_mem_acc(line) is not None:
            self.__update_mem_acc(cycle, uid, line)

        # mem.new_access
        elif tr.parse_mem_new(line) is not None:
            self.__update_mem_new(cycle, uid, line)

        # mem.end_access
        elif tr.parse_mem_end(line) is not None:
            self.__update_mem_end(cycle, uid)
