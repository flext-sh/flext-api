"""Thread-safe pipeline storage for FLEXT API."""

import threading
import uuid
from typing import Any, Optional


class ThreadSafePipelineStorage:
    """Thread-safe in-memory storage for pipelines."""

    def __init__(self) -> None:
        """Initialize storage with thread safety."""
        self._pipelines: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    def create_pipeline(self, pipeline_data: dict[str, Any]) -> str:
        """Create a new pipeline and return its ID."""
        with self._lock:
            pipeline_id = pipeline_data.get("id", str(uuid.uuid4()))
            self._pipelines[pipeline_id] = {
                **pipeline_data,
                "id": pipeline_id,
                "created_at": "2025-06-30T02:00:00Z",
                "status": "created",
            }
            return pipeline_id

    def get_pipeline(self, pipeline_id: str) -> Optional[dict[str, Any]]:
        """Get pipeline by ID."""
        with self._lock:
            return self._pipelines.get(pipeline_id)

    def list_pipelines(self) -> list[dict[str, Any]]:
        """List all pipelines."""
        with self._lock:
            return list(self._pipelines.values())

    def update_pipeline(self, pipeline_id: str, updates: dict[str, Any]) -> bool:
        """Update pipeline data."""
        with self._lock:
            if pipeline_id in self._pipelines:
                self._pipelines[pipeline_id].update(updates)
                return True
            return False

    def delete_pipeline(self, pipeline_id: str) -> bool:
        """Delete pipeline by ID."""
        with self._lock:
            if pipeline_id in self._pipelines:
                del self._pipelines[pipeline_id]
                return True
            return False
