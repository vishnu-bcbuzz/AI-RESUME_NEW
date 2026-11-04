"""Persistent Round Robin Resume Template Scheduler for FUTRSEC.

Ensures deterministic, sequential template selection across application restarts.
Thread-safe, concurrency-guarded, with assignment tracking and role-eligibility support.
"""

import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field

from app.config import settings
from app.reports.templates import template_registry, ResumeTemplate

logger = logging.getLogger("futrsec.round_robin")


class TemplateAssignmentRecord(BaseModel):
    job_id: str
    template_id: str
    template_name: str
    role_name: Optional[str] = None
    assigned_at: str
    status: str = "assigned"  # assigned, completed, failed
    output_format: str = "docx"
    retry_count: int = 0


class RoundRobinScheduler:
    """Thread-safe, persistent Round Robin template scheduler."""

    def __init__(
        self,
        state_file: Optional[Path] = None,
        assignments_file: Optional[Path] = None,
        registry=template_registry,
    ):
        self.state_file = state_file or (settings.TEMPLATES_STORAGE_DIR / "round_robin_state.json")
        self.assignments_file = assignments_file or (settings.TEMPLATES_STORAGE_DIR / "assignments.json")
        self.registry = registry
        self._lock = threading.RLock()
        self._cursor = 0
        self._load_state()

    def _load_state(self) -> None:
        """Loads cursor and assignment state from disk."""
        with self._lock:
            if self.state_file.exists():
                try:
                    with open(self.state_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self._cursor = int(data.get("cursor", 0))
                        logger.info("Loaded persistent Round Robin cursor: %d", self._cursor)
                except Exception as exc:
                    logger.warning("Could not read cursor state file, resetting to 0: %s", exc)
                    self._cursor = 0
            else:
                self._cursor = 0
                self._save_state()

    def _save_state(self) -> None:
        """Atomically persists cursor state to disk."""
        with self._lock:
            temp_file = self.state_file.with_suffix(".tmp")
            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump({"cursor": self._cursor, "updated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)
                temp_file.replace(self.state_file)
            except Exception as exc:
                logger.error("Failed to save Round Robin state: %s", exc)

    def select_next_template(
        self,
        role_name: Optional[str] = None,
        job_id: Optional[str] = None,
        output_format: str = "docx",
    ) -> Tuple[ResumeTemplate, TemplateAssignmentRecord]:
        """Atomically selects the next eligible template in the Round Robin sequence.

        If a job_id already exists in assignment records, reuses the assigned template
        to ensure retry consistency without advancing the global cursor.
        """
        with self._lock:
            actual_job_id = job_id or f"gen_{uuid.uuid4().hex[:12]}"

            # Check if this job_id was already assigned (idempotent retry policy)
            existing_record = self._find_assignment(actual_job_id)
            if existing_record:
                template = self.registry.get_template(existing_record.template_id)
                if template and template.is_active:
                    existing_record.retry_count += 1
                    self._update_assignment(existing_record)
                    logger.info("Reusing existing template %s for retry job %s", template.template_id, actual_job_id)
                    return template, existing_record

            # Get eligible active templates
            eligible = self.registry.get_eligible_templates(role_name)
            if not eligible:
                raise RuntimeError(
                    f"No active resume templates are eligible for selection (role: '{role_name or 'any'}')."
                )

            # Round Robin selection with modular arithmetic wraparound
            index = self._cursor % len(eligible)
            selected_template = eligible[index]

            # Advance cursor atomically
            self._cursor = (self._cursor + 1) % 1000000000
            self._save_state()

            # Record assignment
            assignment = TemplateAssignmentRecord(
                job_id=actual_job_id,
                template_id=selected_template.template_id,
                template_name=selected_template.template_name,
                role_name=role_name,
                assigned_at=datetime.now(timezone.utc).isoformat(),
                status="assigned",
                output_format=output_format,
            )
            self._append_assignment(assignment)

            logger.info(
                "Round Robin assigned template %s to job %s (Sequence position %d)",
                selected_template.template_id, actual_job_id, index
            )
            return selected_template, assignment

    def assign_manual_template(
        self,
        template_id: str,
        role_name: Optional[str] = None,
        job_id: Optional[str] = None,
        output_format: str = "docx",
    ) -> Tuple[ResumeTemplate, TemplateAssignmentRecord]:
        """Atomically assigns a candidate-selected template to a generation job WITHOUT advancing the Round Robin cursor.

        If a job_id already exists in assignment records, reuses the assigned template
        to ensure retry consistency. Validates that the requested template is active and registered.
        """
        with self._lock:
            actual_job_id = job_id or f"gen_{uuid.uuid4().hex[:12]}"

            # Check if this job_id was already assigned (idempotent retry policy)
            existing_record = self._find_assignment(actual_job_id)
            if existing_record:
                template = self.registry.get_template(existing_record.template_id)
                if template and template.is_active:
                    existing_record.retry_count += 1
                    self._update_assignment(existing_record)
                    logger.info("Reusing existing template %s for retry job %s", template.template_id, actual_job_id)
                    return template, existing_record

            template = self.registry.get_template(template_id)
            if not template or not template.is_active:
                raise ValueError(
                    f"Template '{template_id}' is invalid, inactive, or not registered."
                )

            # Record assignment WITHOUT modifying or advancing self._cursor!
            assignment = TemplateAssignmentRecord(
                job_id=actual_job_id,
                template_id=template.template_id,
                template_name=template.template_name,
                role_name=role_name,
                assigned_at=datetime.now(timezone.utc).isoformat(),
                status="assigned",
                output_format=output_format,
            )
            self._append_assignment(assignment)

            logger.info(
                "Manual selection assigned template %s to job %s (Round Robin cursor remains at %d)",
                template.template_id, actual_job_id, self._cursor
            )
            return template, assignment

    def update_job_status(self, job_id: str, status: str) -> None:
        """Updates the status of an assigned resume generation job."""
        with self._lock:
            record = self._find_assignment(job_id)
            if record:
                record.status = status
                self._update_assignment(record)

    def get_current_cursor(self) -> int:
        """Returns current cursor position."""
        with self._lock:
            return self._cursor

    def reset_cursor(self, to_position: int = 0) -> None:
        """Resets the cursor position (primarily for testing and administration)."""
        with self._lock:
            self._cursor = to_position
            self._save_state()

    def _find_assignment(self, job_id: str) -> Optional[TemplateAssignmentRecord]:
        """Finds an existing assignment record by job ID."""
        if not self.assignments_file.exists():
            return None
        try:
            with open(self.assignments_file, "r", encoding="utf-8") as f:
                records = json.load(f)
                if job_id in records:
                    return TemplateAssignmentRecord(**records[job_id])
        except Exception as exc:
            logger.warning("Error reading assignments file: %s", exc)
        return None

    def _append_assignment(self, record: TemplateAssignmentRecord) -> None:
        """Appends an assignment record to disk."""
        records = {}
        if self.assignments_file.exists():
            try:
                with open(self.assignments_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
            except Exception:
                records = {}
        records[record.job_id] = record.model_dump()
        temp_file = self.assignments_file.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
            temp_file.replace(self.assignments_file)
        except Exception as exc:
            logger.error("Failed to append assignment record: %s", exc)

    def _update_assignment(self, record: TemplateAssignmentRecord) -> None:
        self._append_assignment(record)


round_robin_scheduler = RoundRobinScheduler()
