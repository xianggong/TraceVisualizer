#!/usr/bin/python
""" This module contains helper functions to parser Multi2Sim trace """


def parser(keyword, line):
    """ Main parser function """
    try:
        for item in line.split(' '):
            if keyword in item:
                return item.split('=')[1]
    except IndexError:
        return "[ERR] parser: " + line


def parse_as_int(keyword, line):
    """ Decode and return as integer """
    return int(parser(keyword, line))


def parse_as_string(keyword, line):
    """ Decode and return as string, remove redundant characters """
    temp = line.replace('"', '')
    temp = temp.replace('\n', '')
    string = parser(keyword, temp)
    return string


def get_inst_uid(line):
    """ Get instruction unique id """
    return parse_as_string('cu', line) + parse_as_string('id', line)


def get_id(line):
    """ Decode id """
    return int(parser('id', line))


def get_cu(line):
    """ Decode cu """
    return int(parser('cu', line))


def get_ib(line):
    """ Decode ib """
    return int(parser('ib', line))


def get_wg(line):
    """ Decode wg """
    return int(parser('wg', line))


def get_wf(line):
    """ Decode wf """
    return int(parser('wf', line))


def get_uop(line):
    """ Decode uop """
    return int(parser('uop_id', line))


def get_stg(line):
    """ Decode stg """
    if 'si.end_inst' in line:
        return 'end'
    else:
        return parse_as_string('stg', line)


def get_asm(line):
    """ Decode asm """
    return parse_as_string('asm', line)


def get_inst_type(line):
    """ Decode instruction type """
    asm = parse_as_string('asm', line)

    is_scalar = 0
    is_mem = 0
    is_load = 0
    is_ds = 0

    if asm.split('_')[0] == 's':
        is_scalar = 1

    if asm.split('_')[0] == 'ds':
        is_ds = 1

    if 'load' in asm:
        is_mem = 1
        is_load = 1
    elif 'store' in asm:
        is_mem = 1
        is_load = 0

    return is_scalar << 3 + is_mem << 2 + is_load << 1 + is_ds


def get_name(line):
    """ Decode name """
    return parse_as_string('name', line)


def get_addr(line):
    """ Decode addr """
    return parser('addr', line)


def get_type(line):
    """ Decode type """
    return parse_as_string('type', line)


def get_state(line):
    """ Decode state """
    return parse_as_string('state', line)


def get_state_location(line):
    """ Decode state location: L1 or LDS """
    return get_state(line).split(':')[0]


def get_state_action(line):
    """ Decode state action: Load, Store or NC Store """
    return get_state(line).split(':')[1]


def get_access_id(line):
    """ Decode access id """
    return int(get_name(line).split('-')[1])
