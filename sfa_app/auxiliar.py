from pathlib import Path

def get_content(path_to_file: Path):
    with open(path_to_file) as f:
        return f.read()
    