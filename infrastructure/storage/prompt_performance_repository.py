"""
File-based implementation of prompt performance repository.
Provides persistence for prompt performance metrics using JSON storage.
"""

import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import asdict

from generator.core.interfaces.prompt_optimization import IPromptPerformanceRepository
from generator.core.domain.prompt_optimization import (
    PromptPerformanceProfile,
    PromptMetrics,
    PromptUsage,
)
from generator.modules.logger import get_logger

logger = get_logger("prompt_performance_repository")


class FilePromptPerformanceRepository(IPromptPerformanceRepository):
    """File-based implementation of prompt performance repository."""

    def __init__(self, storage_path: str = "generator/cache/prompt_performance.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Ensure the storage file exists with proper structure."""
        if not self.storage_path.exists():
            empty_data = {
                "version": "2.0",
                "created_at": datetime.now().isoformat(),
                "prompt_profiles": {},
                "legacy_data": {},
            }
            self._write_data(empty_data)

    def _read_data(self) -> Dict[str, Any]:
        """Read data from storage file."""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Failed to read storage file: {e}, creating new one")
            self._ensure_storage_exists()
            return self._read_data()

    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write data to storage file."""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to write storage file: {e}")
            raise

    def _convert_legacy_data(
        self, legacy_data: Dict[str, Any]
    ) -> List[PromptPerformanceProfile]:
        """Convert legacy prompt performance data to new format."""
        profiles = []

        for prompt_name, prompt_data in legacy_data.items():
            if not isinstance(prompt_data, dict):
                continue

            # Extract metrics from legacy format
            usage_data = prompt_data.get("usage", {})
            performance_data = prompt_data.get("performance", {})

            # Create usage records
            usage_records = []
            for usage_record in usage_data.get("history", []):
                if isinstance(usage_record, dict):
                    usage_records.append(
                        PromptUsage(
                            timestamp=datetime.fromisoformat(
                                usage_record.get(
                                    "timestamp", datetime.now().isoformat()
                                )
                            ),
                            context=usage_record.get("context", ""),
                            success=usage_record.get("success", True),
                            ai_score=usage_record.get("ai_score"),
                            human_score=usage_record.get("human_score"),
                            execution_time=usage_record.get("execution_time", 0.0),
                            provider=usage_record.get("provider", "unknown"),
                        )
                    )

            # Create metrics
            metrics = PromptMetrics(
                usage_count=performance_data.get("usage_count", len(usage_records)),
                success_rate=performance_data.get("success_rate", 1.0),
                avg_ai_score=performance_data.get("avg_ai_score", 0.0),
                avg_human_score=performance_data.get("avg_human_score", 0.0),
                avg_execution_time=performance_data.get("avg_execution_time", 0.0),
                last_used=datetime.fromisoformat(
                    performance_data.get("last_used", datetime.now().isoformat())
                ),
                confidence_score=performance_data.get("confidence_score", 0.5),
                trend_direction=performance_data.get("trend_direction", "stable"),
            )

            # Create profile
            profile = PromptPerformanceProfile(
                prompt_name=prompt_name,
                context=prompt_data.get("context", ""),
                metrics=metrics,
                usage_history=usage_records,
                metadata=prompt_data.get("metadata", {}),
            )

            profiles.append(profile)

        return profiles

    async def get_profile(
        self, prompt_name: str, context: str = ""
    ) -> Optional[PromptPerformanceProfile]:
        """Get performance profile for a specific prompt (internal method)."""

        def _get_profile():
            data = self._read_data()

            # Try new format first
            profiles_data = data.get("prompt_profiles", {})
            profile_key = f"{prompt_name}:{context}" if context else prompt_name

            if profile_key in profiles_data:
                profile_data = profiles_data[profile_key]
                return self._deserialize_profile(profile_data)

            # Try legacy format
            legacy_data = data.get("legacy_data", {})
            if prompt_name in legacy_data:
                legacy_profiles = self._convert_legacy_data(
                    {prompt_name: legacy_data[prompt_name]}
                )
                if legacy_profiles:
                    # Save converted profile in new format
                    self._save_profiles([legacy_profiles[0]])
                    return legacy_profiles[0]

            return None

        return await asyncio.to_thread(_get_profile)

    async def get_performance_profile(
        self, prompt_name: str, detection_type: str
    ) -> Optional[PromptPerformanceProfile]:
        """Get performance profile for a specific prompt."""
        return await self.get_profile(prompt_name, detection_type)

    async def save_usage(self, usage: PromptUsage) -> None:
        """Save a single prompt usage record."""
        # Get or create profile
        profile = await self.get_profile(usage.prompt_name, usage.detection_type)

        if profile is None:
            # Create new profile
            from generator.core.domain.prompt_optimization import PromptMetrics

            metrics = PromptMetrics(
                success_rate=1.0 if usage.success else 0.0,
                average_score=float(usage.score),
                usage_count=1,
                last_10_scores=[usage.score],
            )

            profile = PromptPerformanceProfile(
                prompt_name=usage.prompt_name,
                detection_type=usage.detection_type,
                metrics=metrics,
                usage_history=[usage],
            )
        else:
            # Update existing profile
            profile.usage_history.append(usage)
            profile._recalculate_metrics()

        await self.save_profile(profile)

    async def get_usage_history(
        self,
        prompt_name: Optional[str] = None,
        detection_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[PromptUsage]:
        """Get usage history with optional filters."""

        def _get_history():
            data = self._read_data()
            all_usage = []

            profiles_data = data.get("prompt_profiles", {})
            for profile_key, profile_data in profiles_data.items():
                profile = self._deserialize_profile(profile_data)

                # Apply filters
                if prompt_name and profile.prompt_name != prompt_name:
                    continue
                if detection_type and profile.detection_type != detection_type:
                    continue

                for usage in profile.usage_history:
                    if since and usage.timestamp < since:
                        continue
                    all_usage.append(usage)

            # Sort by timestamp (newest first)
            all_usage.sort(key=lambda u: u.timestamp, reverse=True)

            # Apply limit
            if limit:
                all_usage = all_usage[:limit]

            return all_usage

        return await asyncio.to_thread(_get_history)

    async def get_performance_trends(
        self, detection_type: str, days: int = 30
    ) -> Dict[str, List[tuple]]:
        """Get performance trends over time (prompt_name -> [(date, success_rate), ...])."""

        def _get_trends():
            cutoff_date = datetime.now() - timedelta(days=days)
            trends = {}

            profiles = []
            data = self._read_data()
            profiles_data = data.get("prompt_profiles", {})

            for profile_key, profile_data in profiles_data.items():
                profile = self._deserialize_profile(profile_data)
                if profile.detection_type == detection_type:
                    profiles.append(profile)

            for profile in profiles:
                daily_stats = {}

                for usage in profile.usage_history:
                    if usage.timestamp < cutoff_date:
                        continue

                    day = usage.timestamp.date()
                    if day not in daily_stats:
                        daily_stats[day] = {"total": 0, "success": 0}

                    daily_stats[day]["total"] += 1
                    if usage.success:
                        daily_stats[day]["success"] += 1

                # Convert to trend data
                trend_data = []
                for day, stats in sorted(daily_stats.items()):
                    success_rate = (
                        stats["success"] / stats["total"] if stats["total"] > 0 else 0.0
                    )
                    trend_data.append((day, success_rate))

                if trend_data:
                    trends[profile.prompt_name] = trend_data

            return trends

        return await asyncio.to_thread(_get_trends)

    async def delete_old_usage_records(self, older_than: datetime) -> int:
        """Delete usage records older than specified date. Returns count deleted."""

        def _delete_old():
            data = self._read_data()
            profiles_data = data.get("prompt_profiles", {})

            total_deleted = 0

            for profile_key, profile_data in profiles_data.items():
                profile = self._deserialize_profile(profile_data)

                original_count = len(profile.usage_history)
                profile.usage_history = [
                    usage
                    for usage in profile.usage_history
                    if usage.timestamp >= older_than
                ]

                deleted_count = original_count - len(profile.usage_history)
                total_deleted += deleted_count

                if deleted_count > 0:
                    # Update metrics and save
                    profile._recalculate_metrics()
                    profiles_data[profile_key] = self._serialize_profile(profile)

            if total_deleted > 0:
                data["prompt_profiles"] = profiles_data
                data["last_updated"] = datetime.now().isoformat()
                self._write_data(data)

            return total_deleted

        return await asyncio.to_thread(_delete_old)

    async def save_profile(self, profile: PromptPerformanceProfile) -> None:
        """Save a performance profile."""
        await self._save_profiles([profile])

    async def _save_profiles(self, profiles: List[PromptPerformanceProfile]) -> None:
        """Save multiple performance profiles."""

        def _save():
            data = self._read_data()
            profiles_data = data.get("prompt_profiles", {})

            for profile in profiles:
                profile_key = (
                    f"{profile.prompt_name}:{profile.detection_type}"
                    if profile.detection_type
                    else profile.prompt_name
                )
                profiles_data[profile_key] = self._serialize_profile(profile)

            data["prompt_profiles"] = profiles_data
            data["last_updated"] = datetime.now().isoformat()
            self._write_data(data)

        await asyncio.to_thread(_save)

    async def get_all_profiles(
        self, detection_type: Optional[str] = None
    ) -> List[PromptPerformanceProfile]:
        """Get all performance profiles, optionally filtered by detection type."""

        def _get_all():
            data = self._read_data()
            profiles = []

            # Load from new format
            profiles_data = data.get("prompt_profiles", {})
            for profile_key, profile_data in profiles_data.items():
                profile = self._deserialize_profile(profile_data)
                if not detection_type or profile.detection_type == detection_type:
                    profiles.append(profile)

            # Load from legacy format if new format is empty
            if not profiles:
                legacy_data = data.get("legacy_data", {})
                if legacy_data:
                    legacy_profiles = self._convert_legacy_data(legacy_data)
                    # Save converted profiles
                    if legacy_profiles:
                        asyncio.create_task(self._save_profiles(legacy_profiles))
                    profiles.extend(legacy_profiles)

            return profiles

        return await asyncio.to_thread(_get_all)

    async def delete_profile(self, prompt_name: str, context: str = "") -> bool:
        """Delete a performance profile."""

        def _delete():
            data = self._read_data()
            profiles_data = data.get("prompt_profiles", {})

            profile_key = f"{prompt_name}:{context}" if context else prompt_name
            if profile_key in profiles_data:
                del profiles_data[profile_key]
                data["prompt_profiles"] = profiles_data
                data["last_updated"] = datetime.now().isoformat()
                self._write_data(data)
                return True
            return False

        return await asyncio.to_thread(_delete)

    async def get_top_performers(
        self, detection_type: str, limit: int = 5, min_usage_count: int = 10
    ) -> List[PromptPerformanceProfile]:
        """Get top performing prompts for detection type."""
        profiles = await self.get_all_profiles(detection_type)

        # Filter by minimum usage count
        filtered_profiles = [
            p for p in profiles if p.metrics.usage_count >= min_usage_count
        ]

        # Sort by success rate, then by confidence score
        sorted_profiles = sorted(
            filtered_profiles,
            key=lambda p: (p.metrics.success_rate, p.metrics.confidence_score),
            reverse=True,
        )

        return sorted_profiles[:limit]

    async def cleanup_old_records(self, max_age_days: int = 30) -> int:
        """Clean up old performance records."""

        def _cleanup():
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            data = self._read_data()
            profiles_data = data.get("prompt_profiles", {})

            cleaned_count = 0
            for profile_key, profile_data in profiles_data.items():
                profile = self._deserialize_profile(profile_data)

                # Filter out old usage records
                original_count = len(profile.usage_history)
                profile.usage_history = [
                    usage
                    for usage in profile.usage_history
                    if usage.timestamp > cutoff_date
                ]

                if len(profile.usage_history) < original_count:
                    # Update metrics based on remaining data
                    profile._recalculate_metrics()
                    profiles_data[profile_key] = self._serialize_profile(profile)
                    cleaned_count += original_count - len(profile.usage_history)

            if cleaned_count > 0:
                data["prompt_profiles"] = profiles_data
                data["last_updated"] = datetime.now().isoformat()
                self._write_data(data)

            return cleaned_count

        return await asyncio.to_thread(_cleanup)

    def _serialize_profile(self, profile: PromptPerformanceProfile) -> Dict[str, Any]:
        """Serialize a profile to dictionary format."""
        # Convert metrics to dict and handle enum serialization
        metrics_dict = asdict(profile.metrics)
        if "trend_direction" in metrics_dict:
            metrics_dict["trend_direction"] = metrics_dict["trend_direction"].value

        # Serialize usage history with datetime conversion
        usage_history = []
        for usage in profile.usage_history:
            usage_dict = asdict(usage)
            usage_dict["timestamp"] = usage_dict["timestamp"].isoformat()
            usage_history.append(usage_dict)

        return {
            "prompt_name": profile.prompt_name,
            "context": profile.detection_type,
            "metrics": metrics_dict,
            "usage_history": usage_history,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.last_updated.isoformat(),
        }

    def _deserialize_profile(self, data: Dict[str, Any]) -> PromptPerformanceProfile:
        """Deserialize a profile from dictionary format."""
        # Deserialize metrics
        metrics_data = data["metrics"]
        if "last_used" in metrics_data:
            metrics_data["last_used"] = datetime.fromisoformat(
                metrics_data["last_used"]
            )

        # Handle enum deserialization
        if "trend_direction" in metrics_data and isinstance(
            metrics_data["trend_direction"], str
        ):
            from generator.core.domain.prompt_optimization import TrendDirection

            try:
                metrics_data["trend_direction"] = TrendDirection(
                    metrics_data["trend_direction"]
                )
            except ValueError:
                metrics_data["trend_direction"] = TrendDirection.UNKNOWN

        metrics = PromptMetrics(**metrics_data)

        # Deserialize usage history
        usage_history = []
        for usage_data in data["usage_history"]:
            usage_data["timestamp"] = datetime.fromisoformat(usage_data["timestamp"])
            usage_history.append(PromptUsage(**usage_data))

        return PromptPerformanceProfile(
            prompt_name=data["prompt_name"],
            detection_type=data["context"],
            metrics=metrics,
            usage_history=usage_history,
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(
                data.get("updated_at", data["created_at"])
            ),
        )
