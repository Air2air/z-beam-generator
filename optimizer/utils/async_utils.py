#!/usr/bin/env python3
"""
Async Utilities for Z-Beam Optimizer

Utilities for handling asynchronous operations and concurrency.
"""

import asyncio
import logging
from typing import Any, Awaitable, List, Optional, TypeVar

T = TypeVar('T')
logger = logging.getLogger(__name__)


async def run_async(coro: Awaitable[T]) -> T:
    """
    Run an async coroutine in a synchronous context.

    Args:
        coro: Coroutine to run

    Returns:
        Result of the coroutine
    """
    try:
        return await coro
    except Exception as e:
        logger.error(f"Async operation failed: {e}")
        raise


async def gather_with_exception_handling(
    tasks: List[Awaitable[Any]],
    return_exceptions: bool = False
) -> List[Any]:
    """
    Gather multiple async tasks with proper exception handling.

    Args:
        tasks: List of awaitable tasks
        return_exceptions: Whether to return exceptions instead of raising them

    Returns:
        List of results (or exceptions if return_exceptions=True)
    """
    if not tasks:
        return []

    try:
        results = await asyncio.gather(*tasks, return_exceptions=return_exceptions)
        return list(results)
    except Exception as e:
        logger.error(f"Task gathering failed: {e}")
        if return_exceptions:
            return [e] * len(tasks)
        raise


async def run_with_timeout(
    coro: Awaitable[T],
    timeout: float,
    default: Optional[T] = None
) -> Optional[T]:
    """
    Run a coroutine with a timeout.

    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds
        default: Default value to return on timeout

    Returns:
        Result of coroutine or default value on timeout
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout} seconds")
        return default
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise


async def run_concurrent(
    tasks: List[Awaitable[T]],
    max_concurrent: Optional[int] = None,
    timeout: Optional[float] = None
) -> List[T]:
    """
    Run tasks with controlled concurrency.

    Args:
        tasks: List of awaitable tasks
        max_concurrent: Maximum number of concurrent tasks
        timeout: Timeout for each task

    Returns:
        List of results
    """
    if max_concurrent is None:
        max_concurrent = len(tasks)

    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def run_with_semaphore(task: Awaitable[T]) -> T:
        async with semaphore:
            if timeout:
                return await run_with_timeout(task, timeout)
            return await task

    try:
        wrapped_tasks = [run_with_semaphore(task) for task in tasks]
        results = await gather_with_exception_handling(wrapped_tasks, return_exceptions=True)
        return results
    except Exception as e:
        logger.error(f"Concurrent execution failed: {e}")
        raise


class AsyncTaskManager:
    """Manager for handling async tasks with lifecycle management."""

    def __init__(self):
        self.tasks: List[asyncio.Task] = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def add_task(self, coro: Awaitable[Any], name: Optional[str] = None) -> asyncio.Task:
        """Add a task to be managed."""
        task = asyncio.create_task(coro, name=name)
        self.tasks.append(task)
        return task

    async def wait_all(self, timeout: Optional[float] = None) -> List[Any]:
        """Wait for all tasks to complete."""
        if not self.tasks:
            return []

        try:
            if timeout:
                done, pending = await asyncio.wait(self.tasks, timeout=timeout)
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                return [await task for task in done]
            else:
                return await gather_with_exception_handling(self.tasks)
        except Exception as e:
            self.logger.error(f"Task waiting failed: {e}")
            raise
        finally:
            self.tasks.clear()

    def cancel_all(self) -> None:
        """Cancel all managed tasks."""
        for task in self.tasks:
            if not task.done():
                task.cancel()
        self.tasks.clear()

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.cancel_all()
        # Wait a bit for tasks to cancel
        await asyncio.sleep(0.1)
