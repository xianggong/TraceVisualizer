#!/usr/bin/python
""" This module contains object describe a line in the trace """

import re
import sqlite3
import traceregex as tr


def inst_scalar_vector(asm):
    """ Instruction scalar or vector type """
    if asm.startswith('s'):
        return 'S'
    else:
        return 'V'


def inst_unit_action(asm):
    """ Instruction memory and action """
    unit_action = '      '
    if asm.startswith('ds'):
        if 'read' in asm:
            return 'LDS LD'
        elif 'write' in asm:
            return 'LDS ST'
        else:
            return 'LDS OT'

    if 'load' in asm:
        return 'MEM LD'
    elif 'store' in asm:
        return 'MEM ST'

    return unit_action


class Instructions(object):
    """Instuctions in trace"""

    def __init__(self):
        self.__instructions = {}

    def __get_inst_by_uid(self, uid):
        if uid in self.__instructions:
            return self.__instructions[uid]
        else:
            return None

    def __update_inst_exe(self, cycle, uid, line):
        inst = self.__get_inst_by_uid(uid)
        info = tr.parse_inst_exe(line).groupdict()
        inst['life_full'] += str(cycle) + str(info['stage']) + ', '

    def __update_inst_new(self, cycle, uid, line):
        self.__instructions[uid] = {}
        inst = self.__get_inst_by_uid(uid)
        info = tr.parse_inst_new(line).groupdict()

        inst['uid'] = uid
        inst['inst_order'] = len(self.__instructions)
        inst['start'] = cycle
        inst['life_full'] = str(cycle) + str(info['stage']) + ', '
        for key, value in info.iteritems():
            if key != 'stage':
                self.__instructions[uid][key] = value
        inst['scalar_vector'] = inst_scalar_vector(info['asm'])
        inst['unit_action'] = inst_unit_action(info['asm'])

    def __update_inst_end(self, cycle, uid):
        inst = self.__instructions[uid]
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
            self.__instructions[uid][key] = value

    def parse(self, cycle, line):
        """Parse a line and return current stage"""
        # si.inst
        uid = tr.get_inst_uid(line)
        if tr.parse_inst_exe(line) is not None:
            self.__update_inst_exe(cycle, uid, line)
            return tr.parse_inst_exe(line).group('stage')

        # si.new_inst
        elif tr.parse_inst_new(line) is not None:
            self.__update_inst_new(cycle, uid, line)
            return tr.parse_inst_new(line).group('stage')

        # si.end_inst
        elif tr.parse_inst_end(line) is not None:
            self.__update_inst_end(cycle, uid)
            return 'end'

        return None

    def write_db(self, db_name):
        """ Write inst to database """
        database = sqlite3.connect(db_name)
        cursor = database.cursor()

        # Create inst table
        sql_create_table = 'CREATE TABLE IF NOT EXISTS inst'
        columns = ('uid INTEGER, id INTEGER, start INTEGER, length INTEGER, '
                   'stall INTEGER, fetch INTEGER, issue INTEGER, '
                   'active INTEGER, cu INTEGER, ib INTEGER, wf INTEGER, '
                   'wg INTEGER, uop_id INTEGER, scalar_vector TEXT, '
                   'unit_action TEXT, life_full TEXT, life_lite TEXT, '
                   'asm TEXT, inst_order INTEGER')
        columns = columns.replace('-', '_')  # - to _

        query = sql_create_table + '(' + columns + ')'
        cursor.execute(query)

        # Insert data
        for index in self.__instructions:
            inst = self.__instructions[index]
            columns = ', '.join(inst.keys())
            placeholders = ':' + ', :'.join(inst.keys())
            placeholders = placeholders.replace('-', '_')  # - to _
            query = 'INSERT INTO inst (%s) VALUES (%s)' % (
                columns, placeholders)
            cursor.execute(query, inst)

        # Save (commit) the changes
        database.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        database.close()


class CycleStatistics(object):
    """CycleStatistics contains stats in each cycle"""

    def __init__(self):
        self.__cycle_info = {}
        self.__stage_count = {}

    def update(self, cycle, stage):
        if stage is not None:
            stage = stage.replace('-', '_')
            # Update stage count dictionary
            try:
                self.__stage_count[stage] += 1
            except KeyError:
                self.__stage_count[stage] = 1

            # Update cycle info dictionary
            try:
                cycle_dict = self.__cycle_info[cycle]
                try:
                    cycle_dict[stage] += 1
                except KeyError:
                    cycle_dict[stage] = 1
            except KeyError:
                self.__cycle_info[cycle] = {}
                self.__cycle_info[cycle][stage] = 1

    def dump(self):
        print self.__cycle_info

    def write_db(self, db_name):
        """ Write inst to database """
        database = sqlite3.connect(db_name)
        cursor = database.cursor()

        stages = sorted(self.__stage_count.keys())

        # Create cycle table, all columns contain integers
        sql_create_table = 'CREATE TABLE IF NOT EXISTS cycle'
        columns = ' INTEGER, '.join(stages) + ' INTEGER'
        columns = columns.replace('-', '_')  # - to _

        query = sql_create_table + '(' + columns + ')'
        cursor.execute(query)

        # Insert data
        for index in self.__cycle_info:
            cycle = self.__cycle_info[index]
            columns = ', '.join(cycle.keys())
            placeholders = ':' + ', :'.join(cycle.keys())
            placeholders = placeholders.replace('-', '_')  # - to _
            query = 'INSERT INTO cycle (%s) VALUES (%s)' % (
                columns, placeholders)
            cursor.execute(query, cycle)

        # Save (commit) the changes
        database.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        database.close()
