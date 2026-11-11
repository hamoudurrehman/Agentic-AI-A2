import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(ROOT_DIR)

for p in [ROOT_DIR, PARENT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)
