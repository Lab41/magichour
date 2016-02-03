import gzip
import re

from magichour.api.local.util.log import get_logger
from magichour.api.local.util.namedtuples import LogLine, Transform

logger = get_logger(__name__)


def get_transforms(file_path):
    """
    Reads transforms from a file and returns a list of Transform named tuples. The output is meant to be fed into
    get_transformed_lines().

    Args:
        file_path: a path to a transforms file. See documentation for proper format for the transforms file.

    Returns:
        transforms: list of Transforms
    """
    transforms = []
    with open(file_path, 'r') as fp:
        next(fp)
        for line in fp:
            t_id, t_type, t_name, t_transform = line.strip().split(',', 3)
            transform = Transform(t_id, t_type, t_name, r''+t_transform, re.compile(r''+t_transform))
            transforms.append(transform)
    return transforms


def get_lines(file_path, ts_start_index, ts_end_index, ts_format=None, skip_num_chars=0):
    # If file ends with .gz open with gzip, otherwise open normally.
    fp = gzip.open(file_path, 'rb') if file_path.lower().endswith('.gz') else open(file_path, 'r')
    for line in fp:
        line = line[skip_num_chars:]
        # Strip out timestamp and use ts_format to create time object.
        ts_str = line[ts_start_index:ts_end_index].strip()
        if ts_format:
            ts = time.mktime(datetime.datetime.strptime(ts_str, ts_format).timetuple())
        else:
            ts = float(ts_str)
        text = line[:ts_start_index].join(line[ts_end_index:]).strip()
        yield LogLine(ts, text, None, None , None)
    fp.close()


def get_transformed_lines(lines, transforms): 
    for logline in lines:
        replaceDict = {}
        transformed = logline.text
        for transform in transforms:
            if transform.type == 'REPLACE':
                replaceList = transform.compiled.findall(transformed)
                if replaceList:
                    replaceDict[transform.name] = replaceList
                transformed = transform.compiled.sub(transform.name, transformed, 0)
            # Handle other transform types here.
            # if transform.type == 'EXAMPLE':
                # do stuff
        yield LogLine(logline.ts, transformed, None, replaceDict, None)