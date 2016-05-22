#!/usr/bin/python
""" Memory report parser for Multi2Sim """
import re
import pandas as pd

INDEX = [
    'ModuleName',
    'ModuleId',

    'Sets',
    'Assoc',
    'Policy',
    'BlockSize',
    'Latency',
    'Ports',

    'Accesses',
    'Hits',
    'Misses',
    'HitRatio',
    'Evictions',
    'Retries',

    'Reads',
    'ReadRetries',
    'BlockingReads',
    'NonBlockingReads',
    'ReadHits',
    'ReadMisses',

    'Writes',
    'WriteRetries',
    'BlockingWrites',
    'NonBlockingWrites',
    'WriteHits',
    'WriteMisses',

    'NCWrites',
    'NCWriteRetries',
    'NCBlockingWrites',
    'NCNonBlockingWrites',
    'NCWriteHits',
    'NCWriteMisses',
    'Prefetches',
    'PrefetchAborts',
    'UselessPrefetches',

    'NoRetryAccesses',
    'NoRetryHits',
    'NoRetryMisses',
    'NoRetryHitRatio',
    'NoRetryReads',
    'NoRetryReadHits',
    'NoRetryReadMisses',
    'NoRetryWrites',
    'NoRetryWriteHits',
    'NoRetryWriteMisses',
    'NoRetryNCWrites',
    'NoRetryNCWriteHits',
    'NoRetryNCWriteMisses',
]


def __parse(report_file):
    """ Parse report """
    report = open(report_file, 'r')
    mem_info = {}
    curr_module = None
    for line in report:
        # Ignore network information
        if 'Network' in line:
            break

        # Get module name
        module = re.search(r'[\[]\s(?P<name>\w+(\-\w+)*)\-(?P<id>\w+)\s[\]]',
                           line)
        module_name = module.groupdict()['name'] if module else None
        module_id = module.groupdict()['id'] if module else None
        if module_name and module_id:
            curr_module = module_name + '-' + module_id
            mem_info[curr_module] = [module_name, module_id]
            continue

        # Process statistic
        field = re.search(
            r'\w+\s=\s(?P<stat_value>(.*))', line)
        if field:
            stat_value = field.groupdict()['stat_value']
            if stat_value != 'LRU':
                if '.' not in stat_value:
                    stat_value = int(stat_value)
                else:
                    stat_value = float(stat_value)
            mem_info[curr_module].append(stat_value)

    dataframe = pd.DataFrame(mem_info, index=INDEX)
    dataframe = dataframe.transpose()
    return dataframe


def get_df(report_file):
    """ Return dataframe of the report """
    return __parse(report_file)
