"""
Repository interfaces for the domain layer.
These define the contracts for data persistence without implementation details.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.entities import ContentGenerationRequest, ContentGenerationResult, GenerationSession
from domain.value_objects import SectionSpec, DetectionResult


class IContentRepository(ABC):
    """Repository interface for content generation requests and results."""
    
    @abstractmethod
    async def save_request(self, request: ContentGenerationRequest) -> str:
        """Save a content generation request and return its ID."""
        pass
    
    @abstractmethod
    async def get_request(self, request_id: str) -> Optional[ContentGenerationRequest]:
        """Get a content generation request by ID."""
        pass
    
    @abstractmethod
    async def save_result(self, result: ContentGenerationResult) -> None:
        """Save a content generation result."""
        pass
    
    @abstractmethod
    async def get_result(self, request_id: str) -> Optional[ContentGenerationResult]:
        """Get a content generation result by request ID."""
        pass
    
    @abstractmethod
    async def get_results_by_material(self, material: str, limit: int = 10) -> List[ContentGenerationResult]:
        """Get recent results for a specific material."""
        pass


class ISessionRepository(ABC):
    """Repository interface for generation sessions."""
    
    @abstractmethod
    async def save_session(self, session: GenerationSession) -> None:
        """Save a generation session."""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[GenerationSession]:
        """Get a generation session by ID."""
        pass
    
    @abstractmethod
    async def get_active_sessions(self) -> List[GenerationSession]:
        """Get all active (incomplete) sessions."""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> None:
        """Delete a generation session."""
        pass


class IPromptRepository(ABC):
    """Repository interface for prompt templates and management."""
    
    @abstractmethod
    async def get_prompt(self, name: str, category: str = None) -> Optional[str]:
        """Get a prompt template by name and optional category."""
        pass
    
    @abstractmethod
    async def save_prompt(self, name: str, content: str, category: str = None) -> None:
        """Save a prompt template."""
        pass
    
    @abstractmethod
    async def list_prompts(self, category: str = None) -> List[str]:
        """List available prompt names, optionally filtered by category."""
        pass
    
    @abstractmethod
    async def delete_prompt(self, name: str, category: str = None) -> None:
        """Delete a prompt template."""
        pass
    
    @abstractmethod
    async def get_section_config(self, section_name: str) -> Optional[SectionSpec]:
        """Get configuration for a specific section."""
        pass


class IDetectionRepository(ABC):
    """Repository interface for detection results and analytics."""
    
    @abstractmethod
    async def save_detection_result(
        self, 
        content_id: str, 
        section_name: str, 
        result: DetectionResult
    ) -> None:
        """Save a detection result."""
        pass
    
    @abstractmethod
    async def get_detection_results(
        self, 
        content_id: str, 
        section_name: str = None
    ) -> List[DetectionResult]:
        """Get detection results for content, optionally filtered by section."""
        pass
    
    @abstractmethod
    async def get_detection_analytics(
        self, 
        start_date: datetime = None, 
        end_date: datetime = None,
        material: str = None
    ) -> Dict[str, Any]:
        """Get detection analytics for the specified time period."""
        pass


class IPerformanceRepository(ABC):
    """Repository interface for performance metrics and analytics."""
    
    @abstractmethod
    async def record_generation_metrics(
        self,
        request_id: str,
        section_name: str,
        metrics: Dict[str, Any]
    ) -> None:
        """Record performance metrics for a generation operation."""
        pass
    
    @abstractmethod
    async def record_api_call(
        self,
        provider: str,
        model: str,
        tokens_used: int,
        response_time_ms: float,
        success: bool
    ) -> None:
        """Record API call metrics."""
        pass
    
    @abstractmethod
    async def get_usage_stats(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get usage statistics for the specified time period."""
        pass
    
    @abstractmethod
    async def get_cost_analysis(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        by_provider: bool = True
    ) -> Dict[str, Any]:
        """Get cost analysis for API usage."""
        pass


class ICacheRepository(ABC):
    """Repository interface for caching operations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = None) -> None:
        """Set a value in cache with optional TTL."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a value from cache."""
        pass
    
    @abstractmethod
    async def clear(self, pattern: str = None) -> None:
        """Clear cache entries, optionally matching a pattern."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        pass
