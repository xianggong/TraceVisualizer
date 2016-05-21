#!/usr/bin/python
""" Memory report parser for Multi2Sim """
import re
import pandas as pd

INDEX = [
    'GPUConf',
    'InstSched',
    'WorkSize',
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
        module = re.search(r'[\[]\s(?P<module_name>\w+\-\w+)\s[\]]', line)
        module_name = module.groupdict()['module_name'] if module else None
        if module_name:
            report_conf = report_file.split('.')[0].split('_')
            mem_info[module_name] = [report_conf[0],
                                     report_conf[2],
                                     report_conf[3],
                                     module_name.split('-')[0],
                                     module_name.split('-')[1]]
            curr_module = module_name
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
