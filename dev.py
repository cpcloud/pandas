#!/usr/bin/env python

import os
import sys
import argparse
import multiprocessing
from subprocess import call, check_call

import nose


def tox(args):
    pass


def test(args):
    test_module = args.module
    fast = args.fast
    cover = args.cover
    rebuild = args.rebuild
    noseargs = args.noseargs
    nprocs = args.nprocs

    argv = []

    if rebuild:
        check_call(['python', 'setup.py', 'clean'])
        check_call(['python', 'setup.py', 'build_ext --inplace'])
        check_call(['coverage', 'erase'])

    if fast:
        argv.append('-A "not slow"')

    argv.append('--processes={0}'.format(nprocs))

    if cover:
        argv.append('--with-coverage')

    argv += noseargs

    return nose.main(module=test_module, argv=argv)


def perf(args):
    commits = args.commits
    assert commits is not None
    assert isinstance(commits, list)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(base_dir, 'vb_suite',
                        'test_perf{0}py'.format(os.extsep))
    return call(['python', path] + commits)


def parse_args():
    parser = argparse.ArgumentParser(description=('pandas all-in-one '
                                                  'testing/coverage/'
                                                  'anything-else-that'
                                                  '-falls-under-dev-tools'
                                                  ' script'),
                                     epilog=('The one true dev script to rule'
                                             ' them all'))
    subparsers = parser.add_subparsers()

    tox_parser = subparsers.add_parser('tox',
                                       help='Run tests with a cached build')
    tox_parser.add_argument('-c', '--config', type=argparse.FileType('r'),
                            default='tox.ini')
    tox_parser.add_argument('-p', '--parallel', action='store_true')
    tox_parser.add_argument('-t', '--tests', nargs='+')
    tox_parser.set_defaults(f=tox)

    test_parser = subparsers.add_parser('test', help='Run nosetests')
    test_parser.add_argument('-m', '--module', default='pandas')
    test_parser.add_argument('-f', '--fast', action='store_true')
    test_parser.add_argument('-c', '--cover', action='store_true')
    test_parser.add_argument('-r', '--rebuild', action='store_true')
    test_parser.add_argument('-n', '--nprocs', type=int, default=1)
    test_parser.add_argument('-a', '--noseargs', nargs=argparse.REMAINDER,
                             default=[])
    test_parser.set_defaults(f=test)

    perf_parser = subparsers.add_parser('perf', help='Run vbench')
    perf_parser.add_argument('commits', nargs=2)
    perf_parser.set_defaults(f=perf)

    return parser.parse_args()


if __name__ == '__main__':
    parsed = parse_args()
    sys.exit(parsed.f(parsed))
