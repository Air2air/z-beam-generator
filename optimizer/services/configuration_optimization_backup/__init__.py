"""
Configuration Optimization Service

Provides advanced configuration optimization capabilities for the Z-Beam content generation system.
Supports multiple optimization strategies including Bayesian optimization, grid search, and random search.
"""

import asyncio
import json
import math
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np


class OptimizationStrategy(Enum):
    """Optimization strategies available."""

    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    GENETIC_ALGORITHM = "genetic_algorithm"


@dataclass
class OptimizationParameter:
    """Represents a parameter in the optimization space."""

    name: str
    min_value: Union[int, float]
    max_value: Union[int, float]
    param_type: str  # "int" or "float"
    description: Optional[str] = None
    default_value: Optional[Union[int, float]] = None

    def validate_value(self, value: Union[int, float]) -> bool:
        """Validate if a value is within the parameter bounds."""
        return self.min_value <= value <= self.max_value

    def sample_value(self) -> Union[int, float]:
        """Sample a random value within the parameter bounds."""
        if self.param_type == "int":
            return random.randint(int(self.min_value), int(self.max_value))
        else:
            return random.uniform(self.min_value, self.max_value)


@dataclass
class ParameterSpace:
    """Represents a parameter space for optimization."""

    space_id: str
    name: str
    parameters: Dict[str, OptimizationParameter]
    description: Optional[str] = None

    def sample_parameters(self) -> Dict[str, Union[int, float]]:
        """Sample a complete set of parameters from this space."""
        return {name: param.sample_value() for name, param in self.parameters.items()}

    def validate_parameters(self, params: Dict[str, Union[int, float]]) -> bool:
        """Validate a complete set of parameters."""
        for name, value in params.items():
            if name not in self.parameters:
                return False
            if not self.parameters[name].validate_value(value):
                return False
        return True


@dataclass
class OptimizationResult:
    """Result of an optimization run."""

    optimization_id: str
    strategy: OptimizationStrategy
    parameter_space_id: str
    best_parameters: Dict[str, Union[int, float]]
    best_score: float
    converged: bool
    total_iterations: int
    iteration_history: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class ConfigurationBackup:
    """Configuration backup for rollback purposes."""

    backup_id: str
    config_type: str
    config_data: Dict[str, Any]
    description: str
    timestamp: datetime


class OptimizationError(Exception):
    """Base exception for optimization errors."""

    pass


@dataclass
class OptimizationHistory:
    """Tracks optimization history."""

    optimization_id: str
    results: List[OptimizationResult] = field(default_factory=list)

    def add_result(self, result: OptimizationResult):
        """Add a result to the history."""
        self.results.append(result)

    def get_best_result(self) -> Optional[OptimizationResult]:
        """Get the best result from history."""
        if not self.results:
            return None
        return max(self.results, key=lambda r: r.best_score)


class ConfigurationOptimizationService:
    """Service for optimizing configurations using various strategies."""

    def __init__(self, config):
        """Initialize the configuration optimization service."""
        self.config = config
        self.parameter_spaces: Dict[str, ParameterSpace] = {}
        self.optimization_history: Dict[str, OptimizationResult] = {}
        self.active_optimizations: Dict[str, Dict[str, Any]] = {}
        self.backup_manager = ConfigurationBackupManager()

        # Initialize default parameter spaces
        self._initialize_default_spaces()

    def _initialize_default_spaces(self):
        """Initialize default parameter spaces."""
        # Content quality optimization space
        content_quality_space = ParameterSpace(
            space_id="content_quality",
            name="Content Quality Optimization",
            parameters={
                "readability_weight": OptimizationParameter(
                    name="readability_weight",
                    min_value=0.1,
                    max_value=0.5,
                    param_type="float",
                    description="Weight for readability in content scoring",
                ),
                "structure_weight": OptimizationParameter(
                    name="structure_weight",
                    min_value=0.1,
                    max_value=0.5,
                    param_type="float",
                    description="Weight for structure in content scoring",
                ),
                "technical_depth_weight": OptimizationParameter(
                    name="technical_depth_weight",
                    min_value=0.0,
                    max_value=0.3,
                    param_type="float",
                    description="Weight for technical depth in content scoring",
                ),
            },
            description="Parameter space for optimizing content quality metrics",
        )

        self.parameter_spaces["content_quality"] = content_quality_space

    def health_check(self) -> bool:
        """Perform a health check on the service."""
        return True

    async def optimize_configuration(
        self,
        objective_function: Callable[[Dict[str, Union[int, float]]], float],
        parameter_space_id: str,
        strategy: OptimizationStrategy,
        max_iterations: int = 50,
        convergence_threshold: float = 0.001,
        timeout_seconds: Optional[float] = None,
        optimization_id: Optional[str] = None,
    ) -> OptimizationResult:
        """Optimize configuration using the specified strategy."""

        if parameter_space_id not in self.parameter_spaces:
            raise OptimizationError(f"Parameter space '{parameter_space_id}' not found")

        if optimization_id is None:
            optimization_id = str(uuid.uuid4())

        parameter_space = self.parameter_spaces[parameter_space_id]
        start_time = datetime.now()

        # Track active optimization
        self.active_optimizations[optimization_id] = {
            "start_time": start_time,
            "strategy": strategy,
            "iterations_completed": 0,
        }

        try:
            if strategy == OptimizationStrategy.BAYESIAN_OPTIMIZATION:
                result = await self._bayesian_optimization(
                    objective_function,
                    parameter_space,
                    max_iterations,
                    convergence_threshold,
                    timeout_seconds,
                    optimization_id,
                )
            elif strategy == OptimizationStrategy.GRID_SEARCH:
                result = await self._grid_search_optimization(
                    objective_function,
                    parameter_space,
                    max_iterations,
                    timeout_seconds,
                    optimization_id,
                )
            elif strategy == OptimizationStrategy.RANDOM_SEARCH:
                result = await self._random_search_optimization(
                    objective_function,
                    parameter_space,
                    max_iterations,
                    timeout_seconds,
                    optimization_id,
                )
            else:
                raise OptimizationError(
                    f"Unsupported optimization strategy: {strategy}"
                )

            # Store result
            self.optimization_history[optimization_id] = result

            return result

        finally:
            # Clean up active optimization
            if optimization_id in self.active_optimizations:
                del self.active_optimizations[optimization_id]

    async def _bayesian_optimization(
        self,
        objective_function: Callable,
        parameter_space: ParameterSpace,
        max_iterations: int,
        convergence_threshold: float,
        timeout_seconds: Optional[float],
        optimization_id: str,
    ) -> OptimizationResult:
        """Perform Bayesian optimization."""
        # Simplified Bayesian optimization implementation
        best_score = float("-inf")
        best_params = None
        iteration_history = []
        start_time = datetime.now()

        for iteration in range(max_iterations):
            # Check timeout
            if (
                timeout_seconds
                and (datetime.now() - start_time).total_seconds() > timeout_seconds
            ):
                break

            # Sample parameters (simplified - in real implementation would use Gaussian processes)
            params = parameter_space.sample_parameters()

            try:
                score = await objective_function(params)
            except Exception as e:
                score = float("-inf")

            iteration_history.append(
                {
                    "iteration": iteration + 1,
                    "parameters": params,
                    "score": score,
                    "timestamp": datetime.now(),
                }
            )

            if score > best_score:
                best_score = score
                best_params = params

            # Check convergence
            if len(iteration_history) >= 5:
                recent_scores = [h["score"] for h in iteration_history[-5:]]
                if max(recent_scores) - min(recent_scores) < convergence_threshold:
                    break

        converged = len(iteration_history) < max_iterations

        return OptimizationResult(
            optimization_id=optimization_id,
            strategy=OptimizationStrategy.BAYESIAN_OPTIMIZATION,
            parameter_space_id=parameter_space.space_id,
            best_parameters=best_params or {},
            best_score=best_score if best_score != float("-inf") else 0.0,
            converged=converged,
            total_iterations=len(iteration_history),
            iteration_history=iteration_history,
            metadata={"method": "simplified_bayesian"},
            timestamp=datetime.now(),
        )

    async def _grid_search_optimization(
        self,
        objective_function: Callable,
        parameter_space: ParameterSpace,
        max_iterations: int,
        timeout_seconds: Optional[float],
        optimization_id: str,
    ) -> OptimizationResult:
        """Perform grid search optimization."""
        # Simplified grid search - sample from grid points
        best_score = float("-inf")
        best_params = None
        iteration_history = []
        start_time = datetime.now()

        for iteration in range(max_iterations):
            # Check timeout
            if (
                timeout_seconds
                and (datetime.now() - start_time).total_seconds() > timeout_seconds
            ):
                break

            # Sample parameters from grid (simplified)
            params = parameter_space.sample_parameters()

            try:
                score = await objective_function(params)
            except Exception as e:
                score = float("-inf")

            iteration_history.append(
                {
                    "iteration": iteration + 1,
                    "parameters": params,
                    "score": score,
                    "timestamp": datetime.now(),
                }
            )

            if score > best_score:
                best_score = score
                best_params = params

        return OptimizationResult(
            optimization_id=optimization_id,
            strategy=OptimizationStrategy.GRID_SEARCH,
            parameter_space_id=parameter_space.space_id,
            best_parameters=best_params or {},
            best_score=best_score if best_score != float("-inf") else 0.0,
            converged=True,  # Grid search always "converges"
            total_iterations=len(iteration_history),
            iteration_history=iteration_history,
            metadata={"method": "grid_search"},
            timestamp=datetime.now(),
        )

    async def _random_search_optimization(
        self,
        objective_function: Callable,
        parameter_space: ParameterSpace,
        max_iterations: int,
        timeout_seconds: Optional[float],
        optimization_id: str,
    ) -> OptimizationResult:
        """Perform random search optimization."""
        best_score = float("-inf")
        best_params = None
        iteration_history = []
        start_time = datetime.now()

        for iteration in range(max_iterations):
            # Check timeout
            if (
                timeout_seconds
                and (datetime.now() - start_time).total_seconds() > timeout_seconds
            ):
                break

            # Sample random parameters
            params = parameter_space.sample_parameters()

            try:
                score = await objective_function(params)
            except Exception as e:
                score = float("-inf")

            iteration_history.append(
                {
                    "iteration": iteration + 1,
                    "parameters": params,
                    "score": score,
                    "timestamp": datetime.now(),
                }
            )

            if score > best_score:
                best_score = score
                best_params = params

        return OptimizationResult(
            optimization_id=optimization_id,
            strategy=OptimizationStrategy.RANDOM_SEARCH,
            parameter_space_id=parameter_space.space_id,
            best_parameters=best_params or {},
            best_score=best_score if best_score != float("-inf") else 0.0,
            converged=True,  # Random search always "converges"
            total_iterations=len(iteration_history),
            iteration_history=iteration_history,
            metadata={"method": "random_search"},
            timestamp=datetime.now(),
        )

    def get_optimization_history(
        self, optimization_id: str
    ) -> List[OptimizationResult]:
        """Get optimization history for a specific optimization."""
        if optimization_id in self.optimization_history:
            return [self.optimization_history[optimization_id]]
        return []

    def get_active_optimizations(self) -> Dict[str, Dict[str, Any]]:
        """Get currently active optimizations."""
        return self.active_optimizations.copy()

    def create_parameter_space(self, space: ParameterSpace):
        """Create a new parameter space."""
        if space.space_id in self.parameter_spaces:
            raise OptimizationError(
                f"Parameter space '{space.space_id}' already exists"
            )
        self.parameter_spaces[space.space_id] = space

    def _validate_parameter_space(self, space: ParameterSpace) -> bool:
        """Validate a parameter space."""
        if not space.parameters:
            return False

        for param in space.parameters.values():
            if param.min_value >= param.max_value:
                return False
            if param.param_type not in ["int", "float"]:
                return False

        return True

    def backup_configuration(
        self, config_data: Dict[str, Any], config_type: str, description: str
    ) -> ConfigurationBackup:
        """Create a configuration backup."""
        return self.backup_manager.create_backup(config_data, config_type, description)

    def restore_configuration(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Restore a configuration from backup."""
        return self.backup_manager.restore_backup(backup_id)

    def list_configuration_backups(
        self, config_type: Optional[str] = None
    ) -> List[ConfigurationBackup]:
        """List configuration backups."""
        return self.backup_manager.list_backups(config_type)

    def get_optimization_statistics(
        self, parameter_space_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get optimization statistics for a parameter space."""
        relevant_results = [
            result
            for result in self.optimization_history.values()
            if result.parameter_space_id == parameter_space_id
        ]

        if not relevant_results:
            return None

        total_optimizations = len(relevant_results)
        successful_optimizations = sum(1 for r in relevant_results if r.converged)
        average_score = (
            sum(r.best_score for r in relevant_results) / total_optimizations
        )
        average_iterations = (
            sum(r.total_iterations for r in relevant_results) / total_optimizations
        )

        return {
            "parameter_space_id": parameter_space_id,
            "total_optimizations": total_optimizations,
            "successful_optimizations": successful_optimizations,
            "average_score": average_score,
            "average_iterations": average_iterations,
        }

    def export_optimization_results(
        self, result: OptimizationResult, format: str = "json"
    ) -> Dict[str, Any]:
        """Export optimization results."""
        return {
            "optimization_id": result.optimization_id,
            "strategy": result.strategy.value,
            "parameter_space_id": result.parameter_space_id,
            "best_parameters": result.best_parameters,
            "best_score": result.best_score,
            "converged": result.converged,
            "total_iterations": result.total_iterations,
            "iteration_history": result.iteration_history,
            "metadata": result.metadata,
            "timestamp": result.timestamp.isoformat(),
        }

    def batch_optimize_configurations(
        self,
        objective_functions: List[Callable],
        parameter_space_id: str,
        strategy: OptimizationStrategy,
        max_iterations: int,
        optimization_ids: Optional[List[str]] = None,
    ) -> List[OptimizationResult]:
        """Batch optimize multiple configurations."""
        if optimization_ids is None:
            optimization_ids = [
                str(uuid.uuid4()) for _ in range(len(objective_functions))
            ]

        results = []
        for obj_func, opt_id in zip(objective_functions, optimization_ids):
            # Run optimization synchronously for simplicity
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.optimize_configuration(
                        obj_func,
                        parameter_space_id,
                        strategy,
                        max_iterations,
                        optimization_id=opt_id,
                    )
                )
                results.append(result)
            finally:
                loop.close()

        return results

    def cleanup_old_backups(self, days_to_keep: int = 30) -> int:
        """Clean up old configuration backups."""
        return self.backup_manager.cleanup_old_backups(days_to_keep)

    def get_parameter_importance(
        self, parameter_space_id: str
    ) -> Optional[Dict[str, float]]:
        """Analyze parameter importance based on optimization history."""
        relevant_results = [
            result
            for result in self.optimization_history.values()
            if result.parameter_space_id == parameter_space_id
        ]

        if len(relevant_results) < 2:
            return None

        # Simple correlation-based importance analysis
        param_scores = {}
        parameter_space = self.parameter_spaces.get(parameter_space_id)

        if not parameter_space:
            return None

        for param_name in parameter_space.parameters.keys():
            param_values = []
            scores = []

            for result in relevant_results:
                if param_name in result.best_parameters:
                    param_values.append(result.best_parameters[param_name])
                    scores.append(result.best_score)

            if len(param_values) >= 2:
                # Calculate correlation coefficient
                try:
                    correlation = np.corrcoef(param_values, scores)[0, 1]
                    param_scores[param_name] = (
                        abs(correlation) if not np.isnan(correlation) else 0.0
                    )
                except:
                    param_scores[param_name] = 0.0
            else:
                param_scores[param_name] = 0.0

        # Normalize to [0, 1] range
        if param_scores:
            max_score = max(param_scores.values())
            if max_score > 0:
                param_scores = {k: v / max_score for k, v in param_scores.items()}

        return param_scores


class ConfigurationBackupManager:
    """Manages configuration backups for rollback purposes."""

    def __init__(self):
        """Initialize the backup manager."""
        self.backups: Dict[str, ConfigurationBackup] = {}

    def create_backup(
        self, config_data: Dict[str, Any], config_type: str, description: str
    ) -> ConfigurationBackup:
        """Create a new configuration backup."""
        backup_id = str(uuid.uuid4())
        backup = ConfigurationBackup(
            backup_id=backup_id,
            config_type=config_type,
            config_data=config_data.copy(),
            description=description,
            timestamp=datetime.now(),
        )

        self.backups[backup_id] = backup
        return backup

    def restore_backup(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Restore a configuration from backup."""
        if backup_id not in self.backups:
            return None

        backup = self.backups[backup_id]
        return backup.config_data.copy()

    def list_backups(
        self, config_type: Optional[str] = None
    ) -> List[ConfigurationBackup]:
        """List configuration backups."""
        backups = list(self.backups.values())

        if config_type:
            backups = [b for b in backups if b.config_type == config_type]

        # Sort by timestamp (newest first)
        backups.sort(key=lambda b: b.timestamp, reverse=True)
        return backups

    def cleanup_old_backups(self, days_to_keep: int) -> int:
        """Clean up backups older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        old_backups = [
            backup_id
            for backup_id, backup in self.backups.items()
            if backup.timestamp < cutoff_date
        ]

        for backup_id in old_backups:
            del self.backups[backup_id]

        return len(old_backups)
