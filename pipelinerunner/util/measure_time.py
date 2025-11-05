from time import time
from typing import Callable
from functools import wraps

from pipelinerunner.util.logger import Logger


logger = Logger.get_logger(__name__)


def measure_time(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        elapsed_time = (time() - start_time) / 60
        logger.info(f'Execution completed in {elapsed_time:.2f} minutes.')
        return result
    return wrapper
