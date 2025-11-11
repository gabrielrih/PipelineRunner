from time import time
from typing import Callable
from functools import wraps

from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


def measure_time(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        elapsed = time() - start_time
        if elapsed < 60:
            logger.debug(f"Execution completed in {elapsed:.2f} seconds.")
            return result
        minutes = elapsed / 60
        logger.debug(f"✅ Execution completed in {minutes:.2f} minutes.")
        return result
    return wrapper
