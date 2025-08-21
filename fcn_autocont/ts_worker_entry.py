# fcn_autocont/ts_worker_entry.py
import json, sys, os, sysconfig, importlib.util, multiprocessing

# Windows spawn friendliness
if os.name == 'nt':
    multiprocessing.freeze_support()

# Ensure stdlib 'statistics' is importable in frozen env (PyInstaller quirk sometimes)
stdlib_dir = sysconfig.get_paths().get('stdlib') or ''
stats_path = os.path.join(stdlib_dir, 'statistics.py')
if os.path.isfile(stats_path):
    spec = importlib.util.spec_from_file_location('statistics', stats_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    sys.modules['statistics'] = mod
else:
    import statistics as mod  # noqa: F401

from totalsegmentator import python_api as ts  # heavy import lives in worker only

def main():
    if len(sys.argv) < 2:
        print("Usage: segmentator_worker <args_json_path>", file=sys.stderr)
        sys.exit(2)
    args_path = sys.argv[1]
    with open(args_path, 'r', encoding='utf-8') as f:
        kwargs = json.load(f)
    ts.totalsegmentator(**kwargs)

if __name__ == '__main__':
    main()
