#!/usr/bin/env python
""" Read 2 kernel asm and evaluate merge effectiveness """

import argparse
import re
import itertools
import instructions

PATTERN_INST = re.compile(ur'\t(?P<instruction>\w+)')
PATTERN_SECTION = re.compile(ur'(\.)(?P<section>\w+)(\t(?P<kernel_func>\w+))*')

INST_INFO = instructions.InstructionInfo()

MEM_SAFE_DISTANCE = 6


class Kernel(object):
    """ Kernel contains several kernel functions """

    def __init__(self, file_name):
        self.__file_name = file_name
        self.__kernel_funcs = {}
        with open(file_name) as asm_file:
            self.__file_raw_text = asm_file.readlines()

        kernel_func_raw_text = ''
        for line in self.__file_raw_text:
            kernel_func_raw_text += line
            if "TGID_Z_EN = 1" in line:
                kernel_func = KernelFunc(kernel_func_raw_text)
                kernel_name = kernel_func.get_name()
                self.__kernel_funcs[kernel_name] = kernel_func
                kernel_func_raw_text = ''

    def get_kernel_funcs(self):
        """ Get kernel functions """
        return self.__kernel_funcs

    def get_kernel_func_by_name(self, name):
        """ Get kernel function by name """
        return self.__kernel_funcs[name]

    def get_name(self):
        """ Get name """
        return self.__file_name

    def dump_inst_map(self):
        """ Dump inst function map """
        for name, object in self.__kernel_funcs.iteritems():
            object.dump_inst_map()

    def get_cost(self, func_name):
        """ Get cost of a kernel function """
        return self.__kernel_funcs[func_name].get_cost()

    def get_cost_all(self):
        """ Get cost of all kernel functions """
        aggregate_cost = 0
        for kernel_func in self.__kernel_funcs.values():
            aggregate_cost += kernel_func.get_cost()
        print self.__file_name, aggregate_cost


class KernelFunc(object):
    """ Kernel Function object"""

    def __init__(self, raw_text):
        self.__name = ''
        self.__sections = {}
        self.__inst_info = []

        self.__build_sections(raw_text)
        self.__build_instruction_map()

    def __build_sections(self, raw_text):
        curr_section = ''
        for line in raw_text.splitlines():
            if '//' not in line:
                match_obj = re.search(PATTERN_SECTION, line)
            if match_obj is not None:
                info = match_obj.groupdict()
                curr_section = info['section']
                if info['kernel_func'] is not None:
                    self.__name = info['kernel_func']
                self.__sections[curr_section] = '\n'
            else:
                self.__sections[curr_section] += line + '\n'

    def __build_instruction_map(self):

        # 1st scan
        for line in self.__sections['text'].splitlines():
            match_obj = re.search(PATTERN_INST, line)
            if match_obj is not None:
                inst = match_obj.groupdict()['instruction']
                self.__inst_info.append(list(INST_INFO.get_info(inst)))

        # 2nd scan, adjust value for memory operations based on distance
        previous_mem_index = -1
        for index, value in enumerate(self.__inst_info):
            exec_unit = value[2]
            if exec_unit == 'vector mem':
                # Get distance from last memory operation
                if previous_mem_index != -1:
                    mem_distance = index - previous_mem_index
                else:
                    mem_distance = MEM_SAFE_DISTANCE

                previous_mem_index = index

                if mem_distance < MEM_SAFE_DISTANCE:
                    mem_distant_penalty = (
                        MEM_SAFE_DISTANCE - mem_distance) * 20
                else:
                    mem_distant_penalty = 0
                value[3] += mem_distant_penalty

        # 3rd scan, adjust value based on NDRange size and GPU configuration

    def get_name(self):
        """ Return the name of the kernel function """
        return self.__name

    def get_info(self):
        """ Return the info list """
        return self.__inst_info

    def dump_inst_map(self):
        """ Print inst map """
        for index, value in enumerate(self.__inst_info):
            print index, value

    def get_cost(self):
        """ Get cost """
        cost = 0
        for item in self.__inst_info:
            cost += item[3]
        return cost


def merge_cost(kernel0, kernel1):
    """ Calculate kernel merge cost """
    cost = 0
    for kernel_func_name in kernel0.get_kernel_funcs().keys():
        merge_info = []
        kernel_func_0 = kernel0.get_kernel_func_by_name(kernel_func_name)
        kernel_func_1 = kernel1.get_kernel_func_by_name(kernel_func_name)
        info_0 = kernel_func_0.get_info()
        info_1 = kernel_func_1.get_info()
        max_len = max(len(info_0), len(info_1))
        for index in range(max_len):
            try:
                inst_info_0 = info_0[index]
            except IndexError:
                inst_info_0 = info_1[index]

            try:
                inst_info_1 = info_1[index]
            except IndexError:
                inst_info_1 = info_0[index]

            if inst_info_0[2] == inst_info_1[2]:
                merge_info.append([inst_info_0[0], inst_info_0[3]])
            else:
                avg_cost = abs(inst_info_0[3] - inst_info_1[3]) / 2
                inst = inst_info_0[0] + '/' + inst_info_1[0]
                merge_info.append([inst, avg_cost])
            # print inst_info_0, inst_info_1, merge_info[index]
        for item in merge_info:
            # print item
            cost += int(item[1])
    return (kernel0.get_name(), kernel1.get_name(), cost)


def main():
    """ Main function """
    # Arg parser
    parser = argparse.ArgumentParser(
        description='Multi2Sim combine evaluator')
    parser.add_argument('kernelasm', nargs='+', help='Needs 2 Kernels')

    args = parser.parse_args()

    kernels = []
    for kernel_file in args.kernelasm:
        kernel = Kernel(kernel_file)
        kernels.append(kernel)
        kernel.get_cost_all()

    merge_info = []
    for subset in itertools.combinations(kernels, 2):
        name0, name1, cost = merge_cost(subset[0], subset[1])
        merge_info.append([name0, name1, cost])

    merge_info.sort(key=lambda x: x[2])
    for item in merge_info:
        print item

if __name__ == '__main__':
    main()
