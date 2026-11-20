Migration: Python 2 -> Python 3

What I added
- `tools/convert_py2_to_py3.py`: runs lib2to3 across the repo and creates `.bak` backups.
- `tools/run_conversion.bat`: Windows helper to run the script.

Recommended workflow
1. Review changes with a dry run:
   - `python tools\convert_py2_to_py3.py`
2. If output looks reasonable, apply changes (creates `.bak` files):
   - `python tools\convert_py2_to_py3.py --run`
   or on Windows:
   - `tools\run_conversion.bat --run`
3. Run your test suite under Python 3 and static checks (flake8, mypy, etc.).
4. Manually inspect any remaining issues (bytes/str, iterator semantics, exception chaining, metaclass differences, third-party incompatibilities).

Notes
- The script skips common build and packaging directories. It makes a `.bak` copy of every file it modifies so you can revert or diff easily.
- I can run the conversion for you now (safe: backups created). Reply `yes` to proceed, or `no` to stop.
