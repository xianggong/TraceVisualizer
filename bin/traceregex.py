#!/usr/bin/python
""" This module contains regular expression for trace file """

import re

# eg: c clk=1000
REGEX_CLOCK = re.compile(ur'c clk=(?P<clock>\d+)')

# eg: id=69 cu=0
REGEX_INST_UID = re.compile(ur'id=(?P<id>\d+) cu=(?P<cu>\d+)')

# eg: si.new_inst id=69 cu=0 ib=0 wg=0 wf=5 uop_id=8 stg="f"
#     asm="s_load_dwordx4 s[8:11], s[2:3], 0x60 // 0000022C: C0880358"
REGEX_INST_NEW = re.compile(ur'si.new_inst id=(?P<id>\d+) cu=(?P<cu>\d+) '
                            r'ib=(?P<ib>\d+) wg=(?P<wg>\d+) wf=(?P<wf>\d+) '
                            r'uop_id=(?P<uop_id>\d+) stg="(?P<stage>.+)" '
                            r'asm="(?P<asm>.*)"')

# eg: si.inst id=60 cu=0 wf=4 uop_id=7 stg="su-r"
REGEX_INST_EXE = re.compile(ur'si.inst id=(?P<id>\d+) cu=(?P<cu>\d+) '
                            r'wf=(?P<wf>\d+) uop_id=(?P<uop_id>\d+) '
                            r'stg="(?P<stage>.+)"')


# eg: si.end_inst id=35 cu=3
REGEX_INST_END = re.compile(ur'si.end_inst id=(?P<id>\d+) cu=(?P<cu>\d+)')


# name="A-227"
REGEX_MEM_UID = re.compile(ur'name="A-(?P<id>\d+)"')

# eg: mem.new_access name="A-227" type="load" state="l1-cu02:load" addr=0xc610
REGEX_MEM_NEW = re.compile(ur'mem.new_access name="A-(?P<id>\d+)" '
                           r'type="(?P<type>\w+)" state="(?P<module>[^\"\:]+):'
                           r'(?P<action>[^\"\:]+)" addr=(?P<addr>\w+)')

# eg: mem.access name="A-213" state="l1-cu0:find_and_lock"
REGEX_MEM_ACC = re.compile(ur'mem.access name="A-(?P<id>\d+)" '
                           r'state="(?P<module>[^\"\:]+):(?P<action>\w+)"')

# eg: mem.end_access name="A-16512"
REGEX_MEM_END = re.compile(ur'mem.end_access name="A-(?P<id>\d+)"')

# eg: mem.new_access_block cache="l2-4" access="A-64385" set=37 way=14
REGEX_MEM_NEW_BLK = re.compile(ur'mem.new_access_block '
                               r'cache="(?P<cache>(?P<level>\w+)-'
                               r'(?P<module>\w+))" access="(?P<id>A-\d+)" '
                               r'set=(?P<set>\d+) way=(?P<way>\d+)')

# eg: mem.end_access_block cache="l2-3" access="A-16705" set=101 way=15
REGEX_MEM_END_BLK = re.compile(ur'mem.end_access_block '
                               r'cache="(?P<cache>(?P<level>\w+)-'
                               r'(?P<module>\w+))" access="(?P<id>A-\d+)" '
                               r'set=(?P<set>\d+) way=(?P<way>\d+)')


def parse(regex, line):
    """Parse line"""
    search = re.search(regex, line)
    return search


def parse_clock(line):
    """Parse clock information"""
    search = parse(REGEX_CLOCK, line)
    if search:
        return int(search.group('clock'))
    else:
        return None


def parse_inst_new(line):
    """Parse si.new_inst line"""
    return parse(REGEX_INST_NEW, line)


def parse_inst_exe(line):
    """Parse si.inst line"""
    return parse(REGEX_INST_EXE, line)


def parse_inst_end(line):
    """Parse si.end_inst line"""
    return parse(REGEX_INST_END, line)


def parse_mem_new(line):
    """Parse mem.new_access line"""
    return parse(REGEX_MEM_NEW, line)


def parse_mem_acc(line):
    """Parse mem.access line"""
    return parse(REGEX_MEM_ACC, line)


def parse_mem_end_blk(line):
    """Parse mem.end_access_block line"""
    return parse(REGEX_MEM_END_BLK, line)


def parse_mem_end(line):
    """Parse mem.end_access line"""
    return parse(REGEX_MEM_END, line)


def get_inst_uid(line):
    """Parse instruction unique id"""
    match_obj = parse(REGEX_INST_UID, line)
    if match_obj:
        return match_obj.group('cu') + match_obj.group('id')
    else:
        return None


def get_mem_uid(line):
    """Parse memory access unique id"""
    match_obj = parse(REGEX_MEM_UID, line)
    if match_obj:
        return match_obj.group('id')
    else:
        return None
