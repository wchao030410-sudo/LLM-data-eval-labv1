import sys
from pathlib import Path


def ensure_frontend_paths() -> None:
    current_file = Path(__file__).resolve()
    frontend_dir = current_file.parent
    project_root = frontend_dir.parent

    for path in [project_root, frontend_dir]:
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
