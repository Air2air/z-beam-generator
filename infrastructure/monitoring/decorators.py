"""
Performance monitoring and instrumentation decorators.
"""

import functools
import time
from typing import Any, Callable, TypeVar
from generator.modules.logger import get_logger

F = TypeVar("F", bound=Callable[..., Any])


def monitor_performance(operation_name: str):
    """Decorator to monitor performance of operations."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"[PERF] {operation_name}: {duration:.3f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"[PERF] {operation_name} FAILED: {duration:.3f}s - {str(e)}"
                )
                raise

        return wrapper

    return decorator


def log_api_call(provider: str):
    """Decorator to log API calls."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)

            # Extract prompt length if available
            prompt_length = "unknown"
            if args and isinstance(args[0], str):
                prompt_length = f"{len(args[0])} chars"
            elif "prompt" in kwargs:
                prompt_length = f"{len(kwargs['prompt'])} chars"

            logger.info(f"[API] {provider} | {prompt_length}")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"[PERF] API call to {provider}: {duration:.3f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"[PERF] API call to {provider} FAILED: {duration:.3f}s - {str(e)}"
                )
                raise

        return wrapper

    return decorator


def validate_input(
    validation_func: Callable[[Any], bool], error_message: str = "Invalid input"
):
    """Decorator to validate function inputs."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate the first argument (typically 'self' is skipped)
            if args and len(args) > 1:
                if not validation_func(args[1]):
                    raise ValueError(f"{error_message}: {args[1]}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry operations on failure."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    if attempt == max_retries:
                        logger.error(
                            f"Operation {func.__name__} failed after {max_retries} retries: {str(e)}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {delay}s..."
                    )
                    time.sleep(delay)

        return wrapper

    return decorator
