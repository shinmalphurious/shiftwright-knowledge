from dataclasses import dataclass, field
from typing import Any


# --------------------------------------------------
# Telemetry Layer
# --------------------------------------------------

@dataclass
class TelemetryFinding:

    issue: str

    confidence: float

    corners: list[str] = field(
        default_factory=list
    )

    evidence: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class DrivingAssessment:

    technique_score: float

    setup_score: float

    driver_confidence: float

    setup_confidence: float

    notes: list[str] = field(
        default_factory=list
    )

@dataclass
class DriverSetupAttribution:

    driver_score: float

    setup_score: float

    confidence: float

    rationale: str


# --------------------------------------------------
# Knowledge Layer
# --------------------------------------------------

@dataclass
class SetupLever:

    name: str

    confidence: float

    sources: list[str] = field(
        default_factory=list
    )


@dataclass
class SetupEffect:

    lever: str

    direction: str

    effect: str

    confidence: float = 0.0


@dataclass
class KnowledgePacket:

    query: str

    vehicle: str | None

    manufacturer: str | None

    car_class: str | None

    setup_levers: list[str] = field(
        default_factory=list
    )

    setup_effects: list[str] = field(
        default_factory=list
    )

    evidence: list[dict] = field(
        default_factory=list
    )

    raw_results: list[dict] = field(
        default_factory=list
    )


# --------------------------------------------------
# Recommendation Layer
# --------------------------------------------------

@dataclass
class SetupRecommendation:

    lever: str

    direction: str

    confidence: float

    rationale: str


@dataclass
class RecommendationPackage:

    issue: str

    vehicle: str

    recommendations: list[SetupRecommendation] = field(
        default_factory=list
    )

    telemetry_confidence: float = 0.0

    setup_confidence: float = 0.0


# --------------------------------------------------
# Future Coaching Layer
# --------------------------------------------------

@dataclass
class CoachingInsight:

    summary: str

    likely_driver_issue: bool

    likely_setup_issue: bool

    confidence: float

    supporting_evidence: list[str] = field(
        default_factory=list
    )

@dataclass
class RankedLever:

    lever: str

    score: float

    evidence_count: int

    reasons: list[str] = field(
        default_factory=list
    )

