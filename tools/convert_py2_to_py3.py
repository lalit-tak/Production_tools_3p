#!/usr/bin/env python3
"""
Convert Python 2 code to Python 3 using lib2to3.
Creates `.bak` backups of original files before writing.

Usage:
  python tools\convert_py2_to_py3.py        # dry run (list files)
  python tools\convert_py2_to_py3.py --run  # apply changes (writes files)
"""

import os
import sys
import shutil
from lib2to3.refactor import RefactoringTool, get_fixers_from_package

SKIP_DIRS = {"build", "dist", ".git", "gp_node.egg-info", "bdist.win32", ".venv", "venv", "env", "__pycache__", ".eggs", "docs"}
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

fixers = get_fixers_from_package('lib2to3.fixes')
tool = RefactoringTool(fixers)


def process_file(path, do_write=False):
    if path.endswith('.py.bak'):
        return
    if not path.endswith('.py'):
        return
    print(("DRY-RUN:" if not do_write else "REFRACTOR:"), path)
    if do_write:
        bak = path + '.bak'
        try:
            shutil.copy2(path, bak)
        except Exception as e:
            print('WARNING: failed to create backup for', path, e)
        try:
            tool.refactor_file(path, write=True)
        except Exception as e:
            print('ERROR refactoring', path, e)


def main():
    do_write = '--run' in sys.argv or '--yes' in sys.argv
    count = 0
    for root, dirs, files in os.walk(ROOT, topdown=True):
        # filter dirs in-place to avoid descending into skipped directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.endswith('.egg-info')]
        for f in files:
            p = os.path.join(root, f)
            # skip this conversion script itself
            if os.path.abspath(p) == os.path.abspath(__file__):
                continue
            if p.endswith('.py'):
                process_file(p, do_write)
                count += 1
    print('Processed {} Python files. (write={})'.format(count, do_write))
    if not do_write:
        print('Dry run complete. Re-run with `--run` to apply changes.')


if __name__ == '__main__':
    main()
