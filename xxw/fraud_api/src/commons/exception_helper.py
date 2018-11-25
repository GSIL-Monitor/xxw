import functools
import traceback

from .logger import get_logger

logger = get_logger(__name__)


def handle_func(function):
    """
    异常处理
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        """捕获异常，记录错误日志"""
        try:
            logger.info(f"IN :{function.__name__},Arguments:{args},{kwargs}")
            result = function(*args, **kwargs)
            logger.info(
                f"OUT :{function.__name__},Arguments:{args},{kwargs},Result:{result}"
            )
            return result
        except BaseException:
            # 记录日志
            logger.exception(traceback.format_exc())
            raise

    return wrapper
