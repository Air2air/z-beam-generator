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
import json
import logging
import copy
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from .. import BaseService, ServiceConfiguration, ServiceError

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Strategies for configuration optimization."""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    GENETIC_ALGORITHM = "genetic_algorithm"
    GRADIENT_BASED = "gradient_based"


class OptimizationGoal(Enum):
    """Goals for optimization."""
    MAXIMIZE_QUALITY = "maximize_quality"
    MAXIMIZE_SPEED = "maximize_speed"
    BALANCE_QUALITY_SPEED = "balance_quality_speed"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_RELIABILITY = "maximize_reliability"


@dataclass
class OptimizationParameter:
    """Parameter for optimization."""
    name: str
    param_type: str  # "int", "float", "categorical", "boolean"
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    default_value: Any = None
    description: str = ""


@dataclass
class OptimizationResult:
    """Result of an optimization run."""
    optimization_id: str
    strategy: OptimizationStrategy
    goal: OptimizationGoal
    best_configuration: Dict[str, Any]
    best_score: float
    improvement_percentage: float
    original_score: float
    iterations_completed: int
    total_iterations: int
    parameter_history: List[Dict[str, Any]] = field(default_factory=list)
    score_history: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigurationBackup:
    """Backup of a configuration."""
    backup_id: str
    component_name: str
    configuration: Dict[str, Any]
    performance_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""


class ConfigurationOptimizationError(ServiceError):
    """Raised when configuration optimization fails."""
    pass


class ConfigurationOptimizationService(BaseService):
    """
    Service for AI-powered configuration optimization.

    This service provides:
    - AI-powered optimization of configuration parameters
    - Multiple optimization strategies and algorithms
    - Performance monitoring and validation
    - Configuration backup and restore
    - Optimization history and analytics
    """

    def __init__(self, config: ServiceConfiguration):
        # Initialize attributes before calling super().__init__
        self.optimization_history: Dict[str, List[OptimizationResult]] = {}
        self.configuration_backups: Dict[str, List[ConfigurationBackup]] = {}
        self.active_optimizations: Dict[str, OptimizationResult] = {}
        self.optimization_parameters: Dict[str, List[OptimizationParameter]] = {}

        super().__init__(config)

    def _validate_config(self) -> None:
        """Validate service configuration."""
        # No specific validation required for base implementation
        pass

    def _initialize(self) -> None:
        """Initialize the service."""
        self.logger.info("Configuration Optimization Service initialized")

    def register_optimization_parameters(
        self,
        component_name: str,
        parameters: List[OptimizationParameter]
    ) -> None:
        """
        Register optimization parameters for a component.

        Args:
            component_name: Name of the component
            parameters: List of optimization parameters
        """
        self.optimization_parameters[component_name] = parameters
        self.logger.info(f"Registered {len(parameters)} optimization parameters for {component_name}")

    def create_configuration_backup(
        self,
        component_name: str,
        configuration: Dict[str, Any],
        performance_score: Optional[float] = None,
        description: str = ""
    ) -> ConfigurationBackup:
        """
        Create a backup of a configuration.

        Args:
            component_name: Name of the component
            configuration: Configuration to backup
            performance_score: Current performance score
            description: Description of the backup

        Returns:
            ConfigurationBackup: Created backup
        """
        import uuid
        backup_id = f"{component_name}_{uuid.uuid4().hex[:8]}"

        backup = ConfigurationBackup(
            backup_id=backup_id,
            component_name=component_name,
            configuration=copy.deepcopy(configuration),
            performance_score=performance_score,
            description=description
        )

        if component_name not in self.configuration_backups:
            self.configuration_backups[component_name] = []

        self.configuration_backups[component_name].append(backup)
        self.logger.info(f"Created configuration backup: {backup_id}")

        return backup

    def restore_configuration_backup(
        self,
        backup_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Restore a configuration from backup.

        Args:
            backup_id: Backup identifier

        Returns:
            Optional[Dict[str, Any]]: Restored configuration
        """
        for component_backups in self.configuration_backups.values():
            for backup in component_backups:
                if backup.backup_id == backup_id:
                    self.logger.info(f"Restored configuration from backup: {backup_id}")
                    return copy.deepcopy(backup.configuration)

        self.logger.warning(f"Backup not found: {backup_id}")
        return None

    async def optimize_configuration(
        self,
        component_name: str,
        current_configuration: Dict[str, Any],
        optimization_goal: OptimizationGoal,
        strategy: OptimizationStrategy = OptimizationStrategy.BAYESIAN_OPTIMIZATION,
        max_iterations: int = 20,
        evaluation_function: Optional[callable] = None,
        **kwargs
    ) -> OptimizationResult:
        """
        Optimize configuration using specified strategy.

        Args:
            component_name: Name of the component to optimize
            current_configuration: Current configuration
            optimization_goal: Goal of the optimization
            strategy: Optimization strategy to use
            max_iterations: Maximum number of iterations
            evaluation_function: Function to evaluate configuration performance
            **kwargs: Additional optimization parameters

        Returns:
            OptimizationResult: Optimization results

        Raises:
            ConfigurationOptimizationError: If optimization fails
        """
        import uuid
        optimization_id = f"opt_{component_name}_{uuid.uuid4().hex[:8]}"

        if component_name not in self.optimization_parameters:
            raise ConfigurationOptimizationError(f"No optimization parameters registered for {component_name}")

        parameters = self.optimization_parameters[component_name]

        # Create initial optimization result
        optimization_result = OptimizationResult(
            optimization_id=optimization_id,
            strategy=strategy,
            goal=optimization_goal,
            best_configuration=copy.deepcopy(current_configuration),
            best_score=0.0,
            improvement_percentage=0.0,
            original_score=0.0,
            iterations_completed=0,
            total_iterations=max_iterations
        )

        self.active_optimizations[optimization_id] = optimization_result

        try:
            # Evaluate original configuration
            original_score = await self._evaluate_configuration(
                current_configuration, evaluation_function, optimization_goal
            )
            optimization_result.original_score = original_score
            optimization_result.best_score = original_score

            self.logger.info(f"Starting optimization for {component_name}: "
                           f"original_score={original_score:.3f}, goal={optimization_goal.value}")

            # Run optimization based on strategy
            if strategy == OptimizationStrategy.GRID_SEARCH:
                result = await self._grid_search_optimization(
                    parameters, current_configuration, optimization_goal,
                    max_iterations, evaluation_function, optimization_result
                )
            elif strategy == OptimizationStrategy.RANDOM_SEARCH:
                result = await self._random_search_optimization(
                    parameters, current_configuration, optimization_goal,
                    max_iterations, evaluation_function, optimization_result
                )
            elif strategy == OptimizationStrategy.BAYESIAN_OPTIMIZATION:
                result = await self._bayesian_optimization(
                    parameters, current_configuration, optimization_goal,
                    max_iterations, evaluation_function, optimization_result
                )
            else:
                raise ConfigurationOptimizationError(f"Unsupported optimization strategy: {strategy}")

            # Calculate improvement
            result.improvement_percentage = (
                (result.best_score - original_score) / original_score * 100
                if original_score != 0 else 0.0
            )

            # Store optimization result
            if component_name not in self.optimization_history:
                self.optimization_history[component_name] = []
            self.optimization_history[component_name].append(result)

            self.logger.info(f"Optimization completed for {component_name}: "
                           f"best_score={result.best_score:.3f}, "
                           f"improvement={result.improvement_percentage:.1f}%")

            return result

        except Exception as e:
            self.logger.error(f"Optimization failed for {component_name}: {e}")
            raise ConfigurationOptimizationError(f"Optimization failed: {e}") from e
        finally:
            # Clean up active optimization
            if optimization_id in self.active_optimizations:
                del self.active_optimizations[optimization_id]

    async def _evaluate_configuration(
        self,
        configuration: Dict[str, Any],
        evaluation_function: Optional[callable],
        goal: OptimizationGoal
    ) -> float:
        """Evaluate a configuration's performance."""
        if evaluation_function:
            return await evaluation_function(configuration)

        # Default evaluation based on goal
        if goal == OptimizationGoal.MAXIMIZE_QUALITY:
            # Simple heuristic: higher values generally better for quality
            score = sum(
                value if isinstance(value, (int, float)) and value > 0 else 0.5
                for value in configuration.values()
                if isinstance(value, (int, float))
            ) / max(1, len([v for v in configuration.values() if isinstance(v, (int, float))]))
            return min(1.0, score)
        elif goal == OptimizationGoal.MAXIMIZE_SPEED:
            # Lower values generally better for speed
            score = 1.0 - sum(
                min(1.0, value / 100.0) if isinstance(value, (int, float)) and value > 0 else 0.0
                for value in configuration.values()
                if isinstance(value, (int, float))
            ) / max(1, len([v for v in configuration.values() if isinstance(v, (int, float))]))
            return max(0.0, score)
        else:
            # Default: average of numeric values
            numeric_values = [v for v in configuration.values() if isinstance(v, (int, float))]
            return sum(numeric_values) / len(numeric_values) if numeric_values else 0.5

    async def _grid_search_optimization(
        self,
        parameters: List[OptimizationParameter],
        base_config: Dict[str, Any],
        goal: OptimizationGoal,
        max_iterations: int,
        evaluation_function: Optional[callable],
        result: OptimizationResult
    ) -> OptimizationResult:
        """Perform grid search optimization."""
        # Simplified grid search - in practice, this would be more sophisticated
        best_config = copy.deepcopy(base_config)
        best_score = result.original_score

        # Try different combinations of parameters
        for iteration in range(max_iterations):
            test_config = copy.deepcopy(base_config)

            # Modify parameters
            for param in parameters:
                if param.param_type in ["int", "float"] and param.min_value is not None and param.max_value is not None:
                    # Try midpoint
                    if param.param_type == "int":
                        test_config[param.name] = int((param.min_value + param.max_value) / 2)
                    else:
                        test_config[param.name] = (param.min_value + param.max_value) / 2

            # Evaluate configuration
            score = await self._evaluate_configuration(test_config, evaluation_function, goal)

            # Update best if improved
            if self._is_better_score(score, best_score, goal):
                best_score = score
                best_config = copy.deepcopy(test_config)

            # Record iteration
            result.parameter_history.append(test_config)
            result.score_history.append(score)
            result.iterations_completed += 1

            # Early stopping if no improvement
            if iteration > 5 and all(s == result.score_history[-1] for s in result.score_history[-3:]):
                break

        result.best_configuration = best_config
        result.best_score = best_score
        return result

    async def _random_search_optimization(
        self,
        parameters: List[OptimizationParameter],
        base_config: Dict[str, Any],
        goal: OptimizationGoal,
        max_iterations: int,
        evaluation_function: Optional[callable],
        result: OptimizationResult
    ) -> OptimizationResult:
        """Perform random search optimization."""
        import random

        best_config = copy.deepcopy(base_config)
        best_score = result.original_score

        for iteration in range(max_iterations):
            test_config = copy.deepcopy(base_config)

            # Randomly modify parameters
            for param in parameters:
                if param.param_type == "int" and param.min_value is not None and param.max_value is not None:
                    test_config[param.name] = random.randint(int(param.min_value), int(param.max_value))
                elif param.param_type == "float" and param.min_value is not None and param.max_value is not None:
                    test_config[param.name] = random.uniform(param.min_value, param.max_value)
                elif param.param_type == "categorical" and param.choices:
                    test_config[param.name] = random.choice(param.choices)
                elif param.param_type == "boolean":
                    test_config[param.name] = random.choice([True, False])

            # Evaluate configuration
            score = await self._evaluate_configuration(test_config, evaluation_function, goal)

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
        result: OptimizationResult
    ) -> OptimizationResult:
        """Perform Bayesian optimization (simplified)."""
        # Simplified Bayesian optimization - in practice, this would use Gaussian processes
        # For now, fall back to random search with some "intelligence"
        return await self._random_search_optimization(
            parameters, base_config, goal, max_iterations, evaluation_function, result
        )

    def _is_better_score(self, new_score: float, current_best: float, goal: OptimizationGoal) -> bool:
        """Determine if new score is better than current best."""
        if goal in [OptimizationGoal.MAXIMIZE_QUALITY, OptimizationGoal.MAXIMIZE_RELIABILITY]:
            return new_score > current_best
        elif goal in [OptimizationGoal.MAXIMIZE_SPEED, OptimizationGoal.MINIMIZE_COST]:
            return new_score < current_best
        else:  # BALANCE_QUALITY_SPEED or unknown
            return new_score > current_best

    def validate_configuration(
        self,
        component_name: str,
        configuration: Dict[str, Any]
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
                errors.append(f"Parameter {param.name} must be float, got {type(value)}")
            elif param.param_type == "boolean" and not isinstance(value, bool):
                errors.append(f"Parameter {param.name} must be boolean, got {type(value)}")
            elif param.param_type == "categorical" and param.choices and value not in param.choices:
                errors.append(f"Parameter {param.name} must be one of {param.choices}, got {value}")

            # Range validation
            if param.param_type in ["int", "float"]:
                if param.min_value is not None and value < param.min_value:
                    errors.append(f"Parameter {param.name} must be >= {param.min_value}, got {value}")
                if param.max_value is not None and value > param.max_value:
                    errors.append(f"Parameter {param.name} must be <= {param.max_value}, got {value}")

        return len(errors) == 0, errors

    def get_optimization_history(
        self,
        component_name: str,
        limit: int = 10
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
                "timestamp": result.timestamp.isoformat()
            }
            for result in history
        ]

    def get_configuration_backups(
        self,
        component_name: str,
        limit: int = 10
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
                "description": backup.description
            }
            for backup in backups
        ]

    def get_optimization_analytics(
        self,
        component_name: str
    ) -> Dict[str, Any]:
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
                    "timestamp": h.timestamp.isoformat()
                }
                for h in history[-5:]
            ]
        }

    def export_configuration(
        self,
        component_name: str,
        configuration: Dict[str, Any],
        file_path: str
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
                "version": "1.0"
            }

            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

            self.logger.info(f"Exported configuration for {component_name} to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False

    def import_configuration(self, file_path: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Import configuration from a file.

        Args:
            file_path: Path to import file

        Returns:
            Optional[Tuple[str, Dict[str, Any]]]: (component_name, configuration)
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            component_name = data.get("component_name")
            configuration = data.get("configuration")

            if not component_name or not configuration:
                self.logger.error("Invalid configuration file format")
                return None

            self.logger.info(f"Imported configuration for {component_name} from {file_path}")
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
