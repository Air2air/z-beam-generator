"""
Configuration Optimization Service

This service provides AI-powered configuration optimization capabilities
that can be used by any component in the system. It analyzes performance
data and uses optimization algorithms to improve configuration settings.

Features:
- AI-powered configuration optimization
- Performance-based optimization
- Backup and restore capabilities
- Validation of optimized configurations
- Multi-strategy optimization approaches
- Performance monitoring and analytics
"""

import asyncio
import copy
import json
import logging
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..base import (
    BaseService,
    ServiceConfiguration,
    ServiceConfigurationError,
    ServiceError,
)


class OptimizationStrategy(Enum):
    """Optimization strategies available."""

    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    GRID_SEARCH = "grid_search"


class OptimizationGoal(Enum):
    """Optimization goals."""

    MAXIMIZE_QUALITY = "maximize_quality"
    MAXIMIZE_SPEED = "maximize_speed"
    MAXIMIZE_RELIABILITY = "maximize_reliability"
    MINIMIZE_COST = "minimize_cost"
    BALANCE_QUALITY_SPEED = "balance_quality_speed"


@dataclass
class OptimizationParameter:
    """Parameter for optimization."""

    name: str
    param_type: str  # "int", "float", "categorical", "boolean"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: Optional[List[Any]] = None
    default_value: Optional[Any] = None
    description: str = ""


@dataclass
class OptimizationResult:
    """Result of an optimization run."""

    optimization_id: str
    strategy: OptimizationStrategy
    goal: OptimizationGoal
    original_score: float
    best_score: float = 0.0
    best_configuration: Dict[str, Any] = field(default_factory=dict)
    improvement_percentage: float = 0.0
    iterations_completed: int = 0
    parameter_history: List[Dict[str, Any]] = field(default_factory=list)
    score_history: List[float] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigurationBackup:
    """Configuration backup."""

    backup_id: str
    component_name: str
    configuration: Dict[str, Any]
    performance_score: float
    created_at: datetime
    description: str = ""


class ConfigurationOptimizationService(BaseService):
    """
    Service for AI-powered configuration optimization.

    This service analyzes performance data and uses optimization algorithms
    to improve configuration settings for various components.
    """

    def __init__(self, config: ServiceConfiguration):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

        # Initialize data structures
        self.optimization_parameters: Dict[str, List[OptimizationParameter]] = {}
        self.optimization_history: Dict[str, List[OptimizationResult]] = {}
        self.configuration_backups: Dict[str, List[ConfigurationBackup]] = {}

    def _validate_config(self) -> None:
        """Validate service configuration."""
        if not self.config.name:
            raise ServiceConfigurationError("Service name is required")

    def _initialize(self) -> None:
        """Initialize the service."""
        self.logger.info(
            f"Initializing Configuration Optimization Service: {self.config.name}"
        )
        self._healthy = True

    async def optimize_configuration(
        self,
        component_name: str,
        base_config: Dict[str, Any],
        goal: OptimizationGoal,
        strategy: OptimizationStrategy = OptimizationStrategy.RANDOM_SEARCH,
        max_iterations: int = 50,
        evaluation_function: Optional[callable] = None,
    ) -> OptimizationResult:
        """
        Optimize configuration for a component.

        Args:
            component_name: Name of the component
            base_config: Base configuration to optimize
            goal: Optimization goal
            strategy: Optimization strategy to use
            max_iterations: Maximum number of iterations
            evaluation_function: Function to evaluate configurations

        Returns:
            OptimizationResult: Optimization results
        """
        if component_name not in self.optimization_parameters:
            raise ServiceError(
                f"No parameters registered for component {component_name}"
            )

        parameters = self.optimization_parameters[component_name]

        # Create optimization result
        result = OptimizationResult(
            optimization_id=str(uuid.uuid4()),
            strategy=strategy,
            goal=goal,
            original_score=0.0,  # Would be evaluated
        )

        # Evaluate original configuration
        if evaluation_function:
            result.original_score = await evaluation_function(base_config)

        # Perform optimization based on strategy
        if strategy == OptimizationStrategy.RANDOM_SEARCH:
            result = await self._random_search_optimization(
                parameters,
                base_config,
                goal,
                max_iterations,
                evaluation_function,
                result,
            )
        elif strategy == OptimizationStrategy.BAYESIAN_OPTIMIZATION:
            result = await self._bayesian_optimization(
                parameters,
                base_config,
                goal,
                max_iterations,
                evaluation_function,
                result,
            )
        else:
            raise ServiceError(f"Unsupported optimization strategy: {strategy}")

        # Calculate improvement
        if result.original_score > 0:
            result.improvement_percentage = (
                (result.best_score - result.original_score) / result.original_score
            ) * 100

        # Store in history
        if component_name not in self.optimization_history:
            self.optimization_history[component_name] = []
        self.optimization_history[component_name].append(result)

        return result

    async def _random_search_optimization(
        self,
        parameters: List[OptimizationParameter],
        base_config: Dict[str, Any],
        goal: OptimizationGoal,
        max_iterations: int,
        evaluation_function: Optional[callable],
        result: OptimizationResult,
    ) -> OptimizationResult:
        """Perform random search optimization."""
        best_config = copy.deepcopy(base_config)
        best_score = result.original_score

        for iteration in range(max_iterations):
            test_config = copy.deepcopy(base_config)

            # Randomly modify parameters
            for param in parameters:
                if (
                    param.param_type == "int"
                    and param.min_value is not None
                    and param.max_value is not None
                ):
                    test_config[param.name] = random.randint(
                        int(param.min_value), int(param.max_value)
                    )
                elif (
                    param.param_type == "float"
                    and param.min_value is not None
                    and param.max_value is not None
                ):
                    test_config[param.name] = random.uniform(
                        param.min_value, param.max_value
                    )
                elif param.param_type == "categorical" and param.choices:
                    test_config[param.name] = random.choice(param.choices)
                elif param.param_type == "boolean":
                    test_config[param.name] = random.choice([True, False])

            # Evaluate configuration
            if evaluation_function:
                score = await evaluation_function(test_config)
            else:
                score = 0.0  # Default score

            # Update best if improved
            if self._is_better_score(score, best_score, goal):
                best_score = score
                best_config = copy.deepcopy(test_config)

            # Record iteration
            result.parameter_history.append(test_config)
            result.score_history.append(score)
            result.iterations_completed += 1

        result.best_configuration = best_config
        result.best_score = best_score
        return result

    async def _bayesian_optimization(
        self,
        parameters: List[OptimizationParameter],
        base_config: Dict[str, Any],
        goal: OptimizationGoal,
        max_iterations: int,
        evaluation_function: Optional[callable],
        result: OptimizationResult,
    ) -> OptimizationResult:
        """Perform Bayesian optimization (simplified)."""
        # Simplified Bayesian optimization - in practice, this would use Gaussian processes
        # For now, fall back to random search with some "intelligence"
        return await self._random_search_optimization(
            parameters, base_config, goal, max_iterations, evaluation_function, result
        )

    def _is_better_score(
        self, new_score: float, current_best: float, goal: OptimizationGoal
    ) -> bool:
        """Determine if new score is better than current best."""
        if goal in [
            OptimizationGoal.MAXIMIZE_QUALITY,
            OptimizationGoal.MAXIMIZE_RELIABILITY,
        ]:
            return new_score > current_best
        elif goal in [OptimizationGoal.MAXIMIZE_SPEED, OptimizationGoal.MINIMIZE_COST]:
            return new_score < current_best
        else:  # BALANCE_QUALITY_SPEED or unknown
            return new_score > current_best

    def register_parameters(
        self, component_name: str, parameters: List[OptimizationParameter]
    ) -> None:
        """
        Register optimization parameters for a component.

        Args:
            component_name: Name of the component
            parameters: List of parameters to optimize
        """
        self.optimization_parameters[component_name] = parameters
        self.logger.info(
            f"Registered {len(parameters)} parameters for {component_name}"
        )

    def create_backup(
        self,
        component_name: str,
        configuration: Dict[str, Any],
        performance_score: float,
        description: str = "",
    ) -> str:
        """
        Create a configuration backup.

        Args:
            component_name: Name of the component
            configuration: Configuration to backup
            performance_score: Performance score of the configuration
            description: Optional description

        Returns:
            str: Backup ID
        """
        backup_id = str(uuid.uuid4())
        backup = ConfigurationBackup(
            backup_id=backup_id,
            component_name=component_name,
            configuration=copy.deepcopy(configuration),
            performance_score=performance_score,
            created_at=datetime.now(),
            description=description,
        )

        if component_name not in self.configuration_backups:
            self.configuration_backups[component_name] = []
        self.configuration_backups[component_name].append(backup)

        self.logger.info(f"Created backup {backup_id} for {component_name}")
        return backup_id

    def restore_backup(
        self, component_name: str, backup_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Restore a configuration from backup.

        Args:
            component_name: Name of the component
            backup_id: Backup ID to restore

        Returns:
            Optional[Dict[str, Any]]: Restored configuration
        """
        if component_name not in self.configuration_backups:
            return None

        for backup in self.configuration_backups[component_name]:
            if backup.backup_id == backup_id:
                self.logger.info(f"Restored backup {backup_id} for {component_name}")
                return copy.deepcopy(backup.configuration)

        return None

    def validate_configuration(
        self, component_name: str, configuration: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate a configuration against registered parameters.

        Args:
            component_name: Name of the component
            configuration: Configuration to validate

        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        if component_name not in self.optimization_parameters:
            return False, [f"No parameters registered for component {component_name}"]

        parameters = self.optimization_parameters[component_name]
        errors = []

        for param in parameters:
            if param.name not in configuration:
                if param.default_value is not None:
                    continue  # Use default
                else:
                    errors.append(f"Missing required parameter: {param.name}")
                    continue

            value = configuration[param.name]

            # Type validation
            if param.param_type == "int" and not isinstance(value, int):
                errors.append(f"Parameter {param.name} must be int, got {type(value)}")
            elif param.param_type == "float" and not isinstance(value, (int, float)):
                errors.append(
                    f"Parameter {param.name} must be float, got {type(value)}"
                )
            elif param.param_type == "boolean" and not isinstance(value, bool):
                errors.append(
                    f"Parameter {param.name} must be boolean, got {type(value)}"
                )
            elif (
                param.param_type == "categorical"
                and param.choices
                and value not in param.choices
            ):
                errors.append(
                    f"Parameter {param.name} must be one of {param.choices}, got {value}"
                )

            # Range validation
            if param.param_type in ["int", "float"]:
                if param.min_value is not None and value < param.min_value:
                    errors.append(
                        f"Parameter {param.name} must be >= {param.min_value}, got {value}"
                    )
                if param.max_value is not None and value > param.max_value:
                    errors.append(
                        f"Parameter {param.name} must be <= {param.max_value}, got {value}"
                    )

        return len(errors) == 0, errors

    def get_optimization_history(
        self, component_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get optimization history for a component.

        Args:
            component_name: Name of the component
            limit: Maximum number of results to return

        Returns:
            List[Dict[str, Any]]: Optimization history
        """
        if component_name not in self.optimization_history:
            return []

        history = self.optimization_history[component_name][-limit:]

        return [
            {
                "optimization_id": result.optimization_id,
                "strategy": result.strategy.value,
                "goal": result.goal.value,
                "best_score": result.best_score,
                "improvement_percentage": result.improvement_percentage,
                "iterations_completed": result.iterations_completed,
                "timestamp": result.timestamp.isoformat(),
            }
            for result in history
        ]

    def get_configuration_backups(
        self, component_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get configuration backups for a component.

        Args:
            component_name: Name of the component
            limit: Maximum number of backups to return

        Returns:
            List[Dict[str, Any]]: Configuration backups
        """
        if component_name not in self.configuration_backups:
            return []

        backups = self.configuration_backups[component_name][-limit:]

        return [
            {
                "backup_id": backup.backup_id,
                "performance_score": backup.performance_score,
                "created_at": backup.created_at.isoformat(),
                "description": backup.description,
            }
            for backup in backups
        ]

    def get_optimization_analytics(self, component_name: str) -> Dict[str, Any]:
        """
        Get optimization analytics for a component.

        Args:
            component_name: Name of the component

        Returns:
            Dict[str, Any]: Optimization analytics
        """
        if component_name not in self.optimization_history:
            return {"total_optimizations": 0}

        history = self.optimization_history[component_name]

        if not history:
            return {"total_optimizations": 0}

        improvements = [h.improvement_percentage for h in history]
        avg_improvement = sum(improvements) / len(improvements)

        strategy_counts = {}
        for h in history:
            strategy = h.strategy.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        return {
            "total_optimizations": len(history),
            "average_improvement": avg_improvement,
            "best_improvement": max(improvements) if improvements else 0.0,
            "worst_improvement": min(improvements) if improvements else 0.0,
            "strategy_distribution": strategy_counts,
            "recent_optimizations": [
                {
                    "id": h.optimization_id,
                    "improvement": h.improvement_percentage,
                    "strategy": h.strategy.value,
                    "timestamp": h.timestamp.isoformat(),
                }
                for h in history[-5:]
            ],
        }

    def export_configuration(
        self, component_name: str, configuration: Dict[str, Any], file_path: str
    ) -> bool:
        """
        Export configuration to a file.

        Args:
            component_name: Name of the component
            configuration: Configuration to export
            file_path: Path to export file

        Returns:
            bool: True if export successful
        """
        try:
            export_data = {
                "component_name": component_name,
                "configuration": configuration,
                "exported_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            self.logger.info(
                f"Exported configuration for {component_name} to {file_path}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False

    def import_configuration(
        self, file_path: str
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Import configuration from a file.

        Args:
            file_path: Path to import file

        Returns:
            Optional[Tuple[str, Dict[str, Any]]]: (component_name, configuration)
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            component_name = data.get("component_name")
            configuration = data.get("configuration")

            if not component_name or not configuration:
                self.logger.error("Invalid configuration file format")
                return None

            self.logger.info(
                f"Imported configuration for {component_name} from {file_path}"
            )
            return component_name, configuration

        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return None

    def health_check(self) -> bool:
        """Perform health check."""
        try:
            # Basic health check - service is healthy if it can manage configurations
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
