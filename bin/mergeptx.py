#!/usr/bin/env python
""" Read 2 PTX kernel and merge """

import argparse
import re


class PtxParser(object):
    """PtxParser reads ptx code"""

    def __init__(self, ptx_file):
        # Readlines
        with open(ptx_file) as raw_ptx_file:
            self.raw_text = raw_ptx_file.readlines()

        # Patterns
        self.__pat_func_decl = re.compile(ur'(?P<func_decl>.visible .entry '
                                          ur'(?P<func_name>\w+))')

        self.__pat_lparen = re.compile(ur'\(')
        self.__pat_rparen = re.compile(ur'\)')
        self.__pat_lbrace = re.compile(ur'\{')
        self.__pat_rbrace = re.compile(ur'\}')

    def parse(self):
        kernel = PtxKernel()

        """Parse PTX"""
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
            match_func_decl = re.search(self.__pat_func_decl, line)
            match_lparen = re.search(self.__pat_lparen, line)
            match_rparen = re.search(self.__pat_rparen, line)
            match_lbrace = re.search(self.__pat_lbrace, line)
            match_rbrace = re.search(self.__pat_rbrace, line)
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
                    continue

                if func_param_processing is True:
                    # print line
                    curr_func_params += line
                elif func_ptx_processing is True:
                    # print line
                    curr_func_ptx += line
            else:
                kernel_meta += line

        kernel.set_meta(kernel_meta)

        return kernel


class PtxKernelFunc(object):
    """PtxKernelFunc"""

    def __init__(self, func_decl, func_param, func_body):
        self.func_decl = func_decl
        self.func_param = func_param
        self.func_body = func_body

        self.__pat_func_decl = re.compile(ur'(?P<func_decl>.visible .entry '
                                          ur'(?P<func_name>\w+))')

    def get_name(self):
        """Get name of function"""
        match_func_decl = re.search(self.__pat_func_decl, self.func_decl)
        return match_func_decl.groupdict()['func_name']

    def dump(self):
        """Dump all sections"""
        print self.func_decl
        print '('
        print self.func_param
        print ')'
        print '{'
        print self.func_body
        print '}'


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


def main():
    """ Main function """
    # Arg parser
    parser = argparse.ArgumentParser(
        description='CUDA PTX kernel merger')
    parser.add_argument('files', nargs='+', help='PTX files')

    args = parser.parse_args()

    ptxparser = PtxParser(args.files[0])
    kernel = ptxparser.parse()
    kernel.dump()


if __name__ == '__main__':
    main()
