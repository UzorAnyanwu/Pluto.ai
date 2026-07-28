from pydantic import BaseModel, Field


class EscalationRules(BaseModel):
    always_escalate_intents: list[str] = Field(default_factory=list)
    sentiment_threshold: str | None = Field(default=None, pattern="^(negative|very_negative)$")
    max_clarification_attempts: int = Field(default=3, ge=1)
    transfer_number: str | None = None


class AiAgentConfigResponse(BaseModel):
    id: str
    version: int
    system_prompt: str
    voice_id: str
    language: str
    enabled_tools: list[str]
    escalation_rules: EscalationRules


class AiAgentConfigInput(BaseModel):
    system_prompt: str = Field(max_length=8000)
    voice_id: str
    language: str
    enabled_tools: list[str] = Field(default_factory=list)
    escalation_rules: EscalationRules = Field(default_factory=EscalationRules)
