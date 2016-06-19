#!/usr/bin/env python
""" Read 2 PTX kernels and merge """

import argparse
import itertools
import re

PAT_FUNC_DECL = re.compile(ur'(?P<func_decl>.visible .entry '
                           r'(?P<func_name>\w+))')

PAT_FUNC_REGS = re.compile(ur'\t*.reg\s*.(?P<reg_type>\w+)\s*'
                           r'\%(?P<reg_name>\w+)<'
                           r'(?P<reg_count>\d+)>;')

PAT_LPAREN = re.compile(ur'\(')
PAT_RPAREN = re.compile(ur'\)')
PAT_LBRACE = re.compile(ur'\{')
PAT_RBRACE = re.compile(ur'\}')

PAT_REGISTER = re.compile(ur'\%(?P<reg_name>\D+)(?P<reg_id>\d+)')


class PtxParser(object):
    """PtxParser reads ptx code"""

    def __init__(self, ptx_file):
        # Readlines
        with open(ptx_file) as raw_ptx_file:
            self.raw_text = raw_ptx_file.readlines()

    def parse(self):
        """Parse PTX"""
        kernel = PtxKernel()
        kernel_meta = ''

        curr_func_decl = ''
        curr_func_params = ''
        curr_func_ptx = ''

        paren_list = []
        brace_list = []

        func_processing = False
        func_param_processing = False
        func_ptx_processing = False

        for line in self.raw_text:
            if '//' in line:
                continue
            match_func_decl = re.search(PAT_FUNC_DECL, line)
            match_lparen = re.search(PAT_LPAREN, line)
            match_rparen = re.search(PAT_RPAREN, line)
            match_lbrace = re.search(PAT_LBRACE, line)
            match_rbrace = re.search(PAT_RBRACE, line)
            if match_func_decl is not None:
                curr_func_decl = match_func_decl.groupdict()['func_decl']
                func_processing = True
            if func_processing is True:

                if match_lparen is not None:
                    paren_list.append('(')
                    func_param_processing = True
                    continue

                if match_rparen is not None:
                    paren_list.pop()
                    if len(paren_list) == 0:
                        func_param_processing = False
                        continue
                    else:
                        curr_func_params += line

                if match_lbrace is not None:
                    brace_list.append(line)
                    if len(brace_list) == 1:
                        func_ptx_processing = True
                        continue

                if match_rbrace is not None:
                    brace_list.pop()
                    if len(brace_list) == 0:
                        func_param_processing = False
                        func_processing = False
                        kernel_func = PtxKernelFunc(
                            curr_func_decl, curr_func_params, curr_func_ptx)
                        kernel.add_func(kernel_func)
                        curr_func_decl = ''
                        curr_func_params = ''
                        curr_func_ptx = ''
                    else:
                        curr_func_ptx += line
                    continue

                if func_param_processing is True:
                    curr_func_params += line
                elif func_ptx_processing is True:
                    curr_func_ptx += line
            else:
                kernel_meta += line

        kernel.set_meta(kernel_meta)

        return kernel


class PtxKernelFunc(object):
    """PtxKernelFunc"""

    def __init__(self, func_decl, func_param, func_body=None):
        self.func_decl = func_decl
        self.func_param = func_param
        if func_body is not None:
            self.func_regs, self.func_body = self.__process_body(func_body)

    def __process_body(self, func_ptx):
        func_regs = {}
        func_body = ''

        for line in func_ptx.splitlines():
            match_regs = re.search(PAT_FUNC_REGS, line)
            if match_regs is not None:
                reg_info = match_regs.groupdict()
                reg_type = reg_info['reg_type']
                reg_name = reg_info['reg_name']
                reg_count = reg_info['reg_count']
                func_regs[reg_type] = (reg_name, reg_count)
            else:
                func_body += line + '\n'

        return (func_regs, func_body)

    def __regs_to_ptx(self):
        ptx = ''
        for item in self.func_regs:
            reg_name, reg_count = self.func_regs[item]
            ptx += '\t.reg .'
            ptx += item + ' %' + reg_name + '<' + str(reg_count) + '>;\n'
        return ptx

    def __dump_func_decl(self):
        print self.func_decl
        print '('
        print self.func_param
        print ')'

    def __dump_func_body(self):
        print '{'
        print self.__regs_to_ptx()
        print self.func_body
        print '}'

    def get_name(self):
        """Get name of function"""
        match_func_decl = re.search(PAT_FUNC_DECL, self.func_decl)
        return match_func_decl.groupdict()['func_name']

    def set_regs(self, regs):
        """Set regs"""
        self.func_regs = regs

    def set_body(self, body):
        """Set body"""
        self.func_body = body

    def dump(self):
        """Dump all sections"""
        self.__dump_func_decl()
        self.__dump_func_body()


class PtxKernel(object):
    """PtxKernel"""

    def __init__(self):
        self.kernel_meta = None
        self.kernel_func = {}

    def set_meta(self, meta):
        """Add meta section"""
        self.kernel_meta = meta

    def add_func(self, func):
        """Add kernel functions """
        func_name = func.get_name()
        self.kernel_func[func_name] = func

    def dump(self):
        """Dump"""
        print self.kernel_meta
        for kernel_func in self.kernel_func.values():
            kernel_func.dump()


class KernelMerge(object):
    """KernelMerge"""

    def __init__(self, kernel0, kernel1):
        self.kernel0 = kernel0
        self.kernel1 = kernel1

    def merge(self):
        """Merge 2 kernels"""
        kernel_func_merger = KernelFuncMerger()

        # Meta should be the same
        meta_0 = self.kernel0.kernel_meta
        meta_1 = self.kernel1.kernel_meta
        assert meta_0 == meta_1
        merge_meta = meta_0

        # Merge kernel functions
        merge_funcs = {}
        for kernel_func_name in self.kernel0.kernel_func.keys():
            if kernel_func_name in self.kernel1.kernel_func.keys():
                kernel_func_0 = self.kernel0.kernel_func[kernel_func_name]
                kernel_func_1 = self.kernel1.kernel_func[kernel_func_name]
                merge_kernel_func = kernel_func_merger.merge(
                    kernel_func_0, kernel_func_1)
                # Add to merge_funcs dictionary
                merge_funcs[merge_kernel_func.get_name()] = merge_kernel_func

        # Create merged PTX kernel and return it
        merge_kernel = PtxKernel()
        merge_kernel.set_meta(merge_meta)
        for kernel_func in merge_funcs.values():
            merge_kernel.add_func(kernel_func)
        return merge_kernel


class KernelFuncMerger(object):
    """docstring for KernelFuncMerger"""

    def __init__(self):
        self.uid = 0

    def __merge_registers(self, regs_0, regs_1):
        assert sorted(regs_0) == sorted(regs_1)
        merge_regs = {}
        for item in regs_0:
            reg_name_0, reg_count_0 = regs_0[item]
            reg_name_1, reg_count_1 = regs_1[item]
            assert reg_name_0 == reg_name_1
            merge_count = int(reg_count_0) + int(reg_count_1)

            # # Add 1 predicate and 3 s32 registers
            # if item == 'pred':
            #     merge_count += 1
            # elif item == 's32':
            #     merge_count += 3

            merge_regs[item] = (reg_name_0, str(merge_count))

        return merge_regs

    def __merge_prefix(self):
        # if ctaid < nctaid / 2
        #   entry 0 -> kernel 0
        # else
        #   entry 1 -> kernel 1
        prefix = ''
        prefix += '\t.reg .pred %pm<1>;\n'
        prefix += '\t.reg .s32  %rm<3>;\n\n'
        prefix += '\t// if ctaid < nctaid /2 \n'
        prefix += '\tmov.u32 %rm1, %ctaid.x;\n'
        prefix += '\tmov.u32 %rm2, %nctaid.x;\n'
        prefix += '\tshr.u32 %rm3, %rm2, 1;\n'
        prefix += '\tsetp.ge.u32 %pm1, %rm1, %rm3;\n'
        prefix += '\t@%pm1 bra ENTRY_1;\n'
        prefix += '\tbra.uni ENTRY_0;\n'

        return prefix

    def __update_regs(self, regs, body):
        # Get reg count as base
        regs_base = {}
        for reg_type in regs:
            reg_name, reg_count = regs[reg_type]
            regs_base[reg_name] = int(reg_count)

        updated_body = ''
        for line in body.splitlines():
            match_regs = re.finditer(PAT_REGISTER, line)
            updated_line = line
            if match_regs is not None:
                for item in match_regs:
                    reg_name = item.groupdict()['reg_name']
                    reg_id = item.groupdict()['reg_id']
                    if reg_name in regs_base:
                        new_reg_id = int(reg_id) + regs_base[reg_name]
                        old_reg = reg_name + str(reg_id)
                        new_reg = reg_name + str(new_reg_id)
                        updated_line = updated_line.replace(old_reg, new_reg)
            # print line, updated_line
            updated_body += updated_line + '\n'

        return updated_body

    def __update_label(self, body):
        updated_body = ''
        for line in body.splitlines():
            updated_line = line
            if 'LBB' in line:
                updated_line = updated_line.replace('LBB', 'SKLBB')
            updated_body += updated_line + '\n'
        return updated_body

    def __update_body(self, regs, body):
        updated_body = body
        updated_body = self.__update_regs(regs, updated_body)
        updated_body = self.__update_label(updated_body)

        return updated_body

    def __merge_body(self, kernel_func_0, kernel_func_1):
        merge_body = 'ENTRY_0:\n'
        body_0 = kernel_func_0.func_body
        merge_body += body_0
        merge_body += 'ENTRY_1:\n'
        body_1 = self.__update_body(
            kernel_func_0.func_regs, kernel_func_1.func_body)
        merge_body += body_1

        return merge_body

    def merge(self, kernel_func_0, kernel_func_1):
        """ Merge 2 PTX kernel function """
        # Check if function decleration match
        assert kernel_func_0.func_decl == kernel_func_1.func_decl
        merge_func_decl = kernel_func_0.func_decl

        # Check if params match
        assert kernel_func_0.func_param == kernel_func_1.func_param
        merge_param = kernel_func_0.func_param

        # Combine registers
        merge_regs = self.__merge_registers(
            kernel_func_0.func_regs, kernel_func_1.func_regs)

        # Combine body
        merge_prefix = self.__merge_prefix()
        merge_body = self.__merge_body(kernel_func_0, kernel_func_1)
        merge_ptx = merge_prefix + merge_body

        # Create merged kernel function
        merge_kernel_func = PtxKernelFunc(merge_func_decl, merge_param)
        merge_kernel_func.set_regs(merge_regs)
        merge_kernel_func.set_body(merge_ptx)

        return merge_kernel_func


def main():
    """ Main function """
    # Arg parser
    parser = argparse.ArgumentParser(
        description='CUDA PTX kernel merger')
    parser.add_argument('files', nargs='+', help='PTX files')

    args = parser.parse_args()

    kernels = []
    for ptxfile in args.files:
        kernel = PtxParser(ptxfile).parse()
        kernels.append(kernel)

    merge_kernels = []
    for subset in itertools.combinations(kernels, 2):
        merge_kernel = KernelMerge(subset[0], subset[1]).merge()
        merge_kernel.dump()
        merge_kernels.append(merge_kernel)


if __name__ == '__main__':
    main()
