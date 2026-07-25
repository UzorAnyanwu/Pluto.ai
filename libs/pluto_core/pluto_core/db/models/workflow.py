"""Workflow automation. See docs/architecture/02-data-model.md §2."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pluto_core.db.base import Base, SoftDeleteMixin, TenantScopedMixin, TimestampMixin, UUIDPKMixin
from pluto_core.db.enums import WorkflowRunStatus


class Workflow(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, TenantScopedMixin, Base):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    trigger: Mapped[str] = mapped_column(
        String(100), nullable=False, doc="e.g. call.completed, lead.qualified, booking.created"
    )
    definition: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, doc="DAG of steps: send_sms, update_crm_field, "
        "create_task, call_webhook, escalate_to_human"
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    runs: Mapped[list["WorkflowRun"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")


class WorkflowRun(UUIDPKMixin, TenantScopedMixin, Base):
    """Append-only run history — a workflow that silently fails is worse than one that's visibly
    broken, per docs/architecture/02-data-model.md §2.
    """

    __tablename__ = "workflow_runs"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trigger_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[WorkflowRunStatus] = mapped_column(
        SAEnum(WorkflowRunStatus, name="workflow_run_status", native_enum=True),
        nullable=False,
        default=WorkflowRunStatus.running,
    )
    step_results: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workflow: Mapped["Workflow"] = relationship(back_populates="runs")
