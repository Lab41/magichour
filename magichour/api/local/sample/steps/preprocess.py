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
    lines = preprocess.read_log_file(log_file, *args, **kwargs)
    return lines


def transformed_lines_substep(lines, transforms):
    logger.info("Transforming log lines...")
    transformed_lines = preprocess.get_transformed_lines(lines, transforms)
    return transformed_lines


def _transformed_lines_to_list_substep(transformed_lines):
    return [line for line in transformed_lines]


@log_time
def preprocess_step(log_file, transforms_file, *args, **kwargs):
    transforms = read_transforms_substep(transforms_file)
    lines = read_lines_substep(log_file, *args, **kwargs)
    transformed_lines = transformed_lines_substep(lines, transforms)

    # get_transformed_lines returns a generator. This converts it to a list.
    transformed_lines = _transformed_lines_to_list_substep(transformed_lines)
    return transformed_lines


@log_time
def preprocess_auditd_step(log_file, *args, **kwargs):
    return [line for line in preprocess.read_auditd_file(log_file)]