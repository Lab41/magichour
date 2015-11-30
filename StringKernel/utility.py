import os

def get_files(dirpath):
    """
    Returns a list of all file paths contained in the directory (searches recursively). The file paths returned are absolute paths.

    Args:
        dirname: directory to traverse for file paths

    Returns:
        paths: absolute paths of all file paths contained in the directory (searches recursively).
    """
    paths = []
    for root, _, files in os.walk(dirpath):
        for f in files:
            if f[0] == ".": # skip hidden files
                continue    
            paths.append(os.path.join(root, f))
    return paths

def get_lines(filepath):
    """
    Returns a list of lines in filename. Each line has its leading/ending whitespace stripped.

    Args:
        filename: filename to read

    Returns:
        lines: list of lines in filename w/ leading/ending whitespace stripped
    """
    with open(filepath) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    return lines
