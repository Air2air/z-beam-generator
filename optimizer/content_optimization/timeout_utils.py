"""
Timeout Utilities

Provides timeout and async operation utilities for content optimization.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def run_with_timeout(coro, timeout_seconds: int = 300):
    """Run a coroutine with a timeout to prevent hanging."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error(f"❌ Operation timed out after {timeout_seconds} seconds")
        raise Exception(f"Operation timed out after {timeout_seconds} seconds")
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        raise


def create_timeout_wrapper(func, timeout_seconds: int = 300):
    """Create a wrapper that adds timeout protection to async functions."""

    async def wrapper(*args, **kwargs):
        try:
            # Create a task for the function
            task = asyncio.create_task(func(*args, **kwargs))

            # Wait for completion with timeout
            result = await asyncio.wait_for(task, timeout=timeout_seconds)
            return result
        except asyncio.TimeoutError:
            logger.error(f"❌ {func.__name__} timed out after {timeout_seconds} seconds")
            # Cancel the task if it's still running
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            raise Exception(
                f"{func.__name__} timed out after {timeout_seconds} seconds"
            )
        except Exception as e:
            logger.error(f"❌ {func.__name__} failed: {e}")
            # Cancel the task if it's still running
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            raise

    return wrapper
