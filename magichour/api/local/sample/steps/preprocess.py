from magichour.api.local.modelgen import preprocess
from magichour.api.local.util.log import get_logger, log_time

logger = get_logger(__name__)

def read_transforms_substep(transforms_file):
    # These transforms are tailored to this dataset.
    # You will likely need to write your own transforms for your own data.
    logger.info("Reading transforms from file: %s" % transforms_file)
    transforms = preprocess.get_transforms(transforms_file)
    return transforms


def read_lines_substep(log_file, *args, **kwargs):
    logger.info("Reading log lines from file: %s" % log_file)
    if kwargs.get('gettime_auditd'):
        # Read timestamp in auditd format
        preprocess_read_log_function = preprocess.read_auditd_file
    else:
        preprocess_read_log_function = preprocess.read_log_file
    lines = preprocess_read_log_function(log_file, *args, **kwargs)
    return lines


def transform_lines_substep(lines, transforms):
    logger.info("Transforming log lines...")
    transformed_lines = preprocess.transform_lines(lines, transforms)
    return transformed_lines


def _transformed_lines_to_list_substep(transformed_lines):
    return [line for line in transformed_lines]


@log_time
def preprocess_step(log_file, transforms_file=None, _transforms_cache={}, *args, **kwargs):
    lines = read_lines_substep(log_file, *args, **kwargs)
    if transforms_file:
        if transforms_file in _transforms_cache:
            transforms = _transforms_cache[transforms_file]
        else:
            transforms = _transforms_cache[transforms_file] = read_transforms_substep(transforms_file)
        transformed_lines = transform_lines_substep(lines, transforms)
    elif kwargs.get('type_template_auditd'):
        transformed_lines = lines
    else:
        raise ValueError('transforms_file is required unless type_template_auditd==True')

    # get_transformed_lines returns a generator. This converts it to a list.
    transformed_lines = _transformed_lines_to_list_substep(transformed_lines)

    return transformed_lines