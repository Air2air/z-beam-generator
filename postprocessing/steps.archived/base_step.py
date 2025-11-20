"""Base Step Infrastructure

Provides abstract base class and result contract for all pipeline steps.
Each step has timing, error handling, and consistent input/output patterns.

Created: November 19, 2025
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import time
import logging


@dataclass
class StepResult:
    """Result from any pipeline step"""
    success: bool
    data: Any
    duration_ms: float
    step_name: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseStep(ABC):
    """
    Base class for all pipeline steps.
    
    Provides:
    - Automatic timing
    - Error handling and recovery
    - Input validation
    - Consistent logging
    - StepResult contract
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def execute(self, context: Dict[str, Any]) -> StepResult:
        """
        Execute step with timing and error handling.
        
        Args:
            context: Shared pipeline context with all data
            
        Returns:
            StepResult with success status and data
        """
        start = time.time()
        step_name = self.__class__.__name__
        
        try:
            # Validate inputs
            self._validate_inputs(context)
            
            # Execute logic
            result_data = self._execute_logic(context)
            
            duration = (time.time() - start) * 1000
            
            self.logger.info(f"✅ {step_name} completed in {duration:.1f}ms")
            
            return StepResult(
                success=True,
                data=result_data,
                duration_ms=duration,
                step_name=step_name
            )
            
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.logger.error(f"❌ {step_name} failed after {duration:.1f}ms: {e}")
            
            return StepResult(
                success=False,
                data=None,
                duration_ms=duration,
                step_name=step_name,
                error=str(e)
            )
    
    @abstractmethod
    def _validate_inputs(self, context: Dict[str, Any]):
        """
        Validate required inputs exist in context.
        
        Args:
            context: Pipeline context
            
        Raises:
            ValueError: If required inputs missing or invalid
        """
        pass
    
    @abstractmethod
    def _execute_logic(self, context: Dict[str, Any]) -> Any:
        """
        Execute step-specific logic.
        
        Args:
            context: Pipeline context with all data
            
        Returns:
            Step-specific result data
        """
        pass
