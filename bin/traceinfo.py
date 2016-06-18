#!/usr/bin/env python
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

        return (info['stage'], info['cu'])

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
        if info['cu'] == '11':
            print inst
        return (info['stage'], info['cu'])

    def __update_inst_end(self, cycle, uid, line):
        inst = self.__instructions[uid]
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
            self.__instructions[uid][key] = value

        return ('end', info['cu'])

    def parse(self, cycle, line):
        """Parse a line and return (stage, cu_id)"""
        uid = tr.get_inst_uid(line)

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
    """CycleStatistics contains several CycleStatisticsCU objects"""

    def __init__(self):
        self.__cycle_stats = {}

    def update(self, cycle, stage, cu_id):
        """Update"""
        if cu_id is None:
            return

        try:
            self.__cycle_stats[cu_id].update(cycle, stage)
        except KeyError:
            self.__cycle_stats[cu_id] = CycleStatisticsCU(cu_id)
            self.__cycle_stats[cu_id].update(cycle, stage)

    def write_db(self, db_name):
        """ Write to database """
        for cyclecu in self.__cycle_stats.values():
            cyclecu.write_db(db_name)


class CycleStatisticsCU(object):
    """CycleStatisticsCU contains stats of each cycle for each compute unit"""

    def __init__(self, cu_id):
        self.__cu_id = cu_id
        self.__cycle_info = {}
        self.__stage_count = {}

    def update(self, cycle, stage):
        """ Update cycle statictics"""
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
                self.__cycle_info[cycle]['cycle'] = cycle
                self.__stage_count['cycle'] = 1
                self.__cycle_info[cycle][stage] = 1

    def write_db(self, db_name):
        """ Write inst to database """
        database = sqlite3.connect(db_name)
        cursor = database.cursor()

        stages = sorted(self.__stage_count.keys())

        # Create cycle table, all columns contain integers
        table_name = 'cycle_cu_' + str(self.__cu_id)
        sql_create_table = 'CREATE TABLE IF NOT EXISTS ' + table_name
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
            query = 'INSERT INTO ' + table_name + ' (%s) VALUES (%s)' % (
                columns, placeholders)
            cursor.execute(query, cycle)

        # Save (commit) the changes
        database.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        database.close()


class MemoryAccess(object):
    """Memory access infomation"""

    def __init__(self):
        self.__mem_access = {}
        self.__mod_cycle = {}

    def __update_mem_new(self, cycle, uid, line):
        info = tr.parse_mem_new(line).groupdict()

        # Create an entry in mem access
        self.__mem_access[uid] = {}

        # Update memory access view
        mem_access = self.__mem_access[uid]
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

        # Create an entry in cycle view
        module = info['module']
        self.__mod_cycle[module] = {}

        # Update module cycle view
        mod_cycle = self.__mod_cycle[module]
        mod_cycle[cycle] = {}
        mod_cycle[cycle][info['action']] = 1

    def __update_mem_acc(self, cycle, uid, line):
        info = tr.parse_mem_acc(line).groupdict()

        # Update memory access view
        mem_access = self.__mem_access[uid]
        mem_access_life = str(cycle) + ' ' + \
            info['module'] + ' ' + info['action']
        if 'miss' in info['action']:
            mem_access['miss'] += 1
        mem_access['life_full'].append(mem_access_life)

        # Update cycle view
        # module = info['module']
        # mod_cycle = self.__mod_cycle[module]
        # try:
        #     cycle_stat = mod_cycle[cycle]
        # except KeyError:
        #     mod_cycle[cycle] = {}
        #     cycle_stat = mod_cycle[cycle]

    def __update_mem_end(self, cycle, uid):
        # info = tr.parse_mem_end(line).groupdict()

        mem_access = self.__mem_access[uid]
        mem_access['length'] = cycle - int(mem_access['start'])
        mem_access['life_full'].append(str(cycle) + ' end')

        mem_access_life_full = ', '.join(mem_access['life_full'])
        mem_access['life_full'] = mem_access_life_full

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

    def write_db(self, db_name):
        """ Write inst to database """
        database = sqlite3.connect(db_name)
        cursor = database.cursor()

        # Create mem_access tables
        sql_create_table = 'CREATE TABLE IF NOT EXISTS mem_access'
        columns = ('uid INTEGER, module TEXT, type TEXT, address TEXT, '
                   'start INTEGER, length INTEGER, miss INTEGER, '
                   'life_full TEXT')
        columns = columns.replace('-', '_')  # - to _
        query = sql_create_table + '(' + columns + ')'
        cursor.execute(query)

        # Insert data
        for index in self.__mem_access:
            mem_access = self.__mem_access[index]
            columns = ', '.join(mem_access.keys())
            placeholders = ':' + ', :'.join(mem_access.keys())
            placeholders = placeholders.replace('-', '_')  # - to _
            query = 'INSERT INTO mem_access' + ' (%s) VALUES (%s)' % (
                columns, placeholders)
            cursor.execute(query, mem_access)

        # Save (commit) the changes
        database.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        database.close()
