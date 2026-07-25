"""Knowledge base / RAG storage. See docs/architecture/02-data-model.md §2 and
docs/architecture/03-ai-and-voice-architecture.md §4.
"""

import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pluto_core.db.base import Base, SoftDeleteMixin, TenantScopedMixin, TimestampMixin, UUIDPKMixin
from pluto_core.db.enums import KnowledgeSourceStatus, KnowledgeSourceType

# OpenAI text-embedding-3-small / Google/Anthropic-compatible embedding dimensionality used
# platform-wide, per the model router in docs/architecture/03-ai-and-voice-architecture.md §3 —
# a single fixed dimensionality avoids needing per-tenant variable-width vector columns.
EMBEDDING_DIM = 1536


class KnowledgeSource(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, TenantScopedMixin, Base):
    __tablename__ = "knowledge_sources"

    type: Mapped[KnowledgeSourceType] = mapped_column(
        SAEnum(KnowledgeSourceType, name="knowledge_source_type", native_enum=True), nullable=False
    )
    status: Mapped[KnowledgeSourceStatus] = mapped_column(
        SAEnum(KnowledgeSourceStatus, name="knowledge_source_status", native_enum=True),
        nullable=False,
        default=KnowledgeSourceStatus.pending,
    )
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class KnowledgeChunk(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    """`business_id` is denormalized onto every chunk (not just reachable via `source_id` join)
    specifically because every retrieval query filters directly on it — see the AI architecture
    doc §4. Denormalizing here means the RLS policy and the HNSW similarity index can both use
    `business_id` directly without a join.
    """

    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        # pgvector's HNSW access method does not support multicolumn indexes (confirmed against
        # a real Postgres instance while building this migration — the originally-designed
        # composite (business_id, embedding) index errors with "access method hnsw does not
        # support multicolumn indexes"). Tenant scoping for retrieval therefore comes from the
        # RLS policy + the btree `business_id` index (from TenantScopedMixin) filtering the
        # candidate set, while this single-column HNSW index handles the ANN search itself —
        # standard practice for pgvector at this data volume (each tenant's slice is small; see
        # docs/architecture/03-ai-and-voice-architecture.md §4). Table partitioning by
        # business_id, with one HNSW index per partition, is the documented future scaling path
        # if a single global index ever becomes the bottleneck.
        Index(
            "ix_knowledge_chunks_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    source: Mapped["KnowledgeSource"] = relationship(back_populates="chunks")
