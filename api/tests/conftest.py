import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(ROOT_DIR, ".."))

for path in (WORKSPACE_ROOT, ROOT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)
