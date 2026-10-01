# Shiftwright Knowledge

A structured iRacing engineering knowledge and setup recommendation engine.

---

# Overview

Shiftwright Knowledge converts iRacing vehicle manuals into a searchable engineering knowledge base capable of producing setup recommendations from telemetry findings.

The goal is to separate:

```text
Telemetry Analysis
```

from:

```text
Engineering Knowledge
```

allowing Shiftwright to focus on identifying vehicle behaviour while the knowledge system focuses on understanding setup adjustments and their effects.

---

# Architecture

```text
PDF Manuals
    ↓
Text Extraction
    ↓
Metadata Classification
    ↓
Chunk Generation
    ↓
Embeddings
    ↓
Semantic Search
    ↓
Knowledge Extraction
    ↓
Lever Ranking
    ↓
Engineering Reasoning
    ↓
Engineering Advisor
```

---

# Repository Structure

```text
shiftwright-knowledge/

├── pdf/
│   Original PDF manuals
│
├── text/
│   Extracted manual text
│
├── metadata/
│   Vehicle metadata
│
├── chunks/
│   Searchable chunks
│
├── indexes/
│   Search indexes
│
├── tools/
│
│   extract_manual_text.py
│   build_metadata.py
│   build_chunks.py
│   build_embeddings.py
│   build_search_index.py
│
│   manual_service.py
│   knowledge_builder.py
│   knowledge_ranker.py
│   knowledge_reasoner.py
│
│   engineering_models.py
│   engineering_advisor.py
│   telemetry_scoring.py
│   driver_setup_attribution.py
│
└── README.md
```

---

# Core Components

## manual_service.py

Provides context-aware semantic search over the manual corpus.

Example:

```python
results = search(
    "entry understeer",
    context=context
)
```

---

## knowledge_builder.py

Extracts:

- Setup levers
- Engineering effects
- Supporting evidence

from retrieved manual content.

Example output:

```text
Anti-Roll Bar
Differential
Differential Preload
Ride Height
Aero Balance
```

---

## knowledge_ranker.py

Ranks setup levers according to issue type.

Examples:

```text
Entry Understeer
Mid-Corner Understeer
Exit Understeer
Entry Oversteer
Poor Rotation
```

Output:

```text
1 Differential Preload
2 Anti-Roll Bar
3 Aero Balance
```

---

## knowledge_reasoner.py

Converts ranked setup levers into engineered setup recommendations.

Example:

```text
Differential Preload
Direction: Decrease

Anti-Roll Bar
Direction: Soften Front
```

---

## driver_setup_attribution.py

Determines whether a telemetry issue appears to be:

```text
Driver-driven
```

or

```text
Setup-driven
```

Example:

```text
Driver Score: 0.78
Setup Score: 0.22
```

---

## telemetry_scoring.py

Produces telemetry-derived findings.

Example:

```python
TelemetryFinding(
    issue="entry understeer",
    confidence=0.73
)
```

Evidence:

```python
{
    "trail_braking_quality": 0.85,
    "steering_saturation": 0.75,
    "rotation_score": 0.61,
    "lap_consistency": 0.84
}
```

---

## engineering_advisor.py

Primary integration point.

This is the only component that external projects should call directly.

Example:

```python
from engineering_advisor import advise

package = advise(
    finding,
    context
)
```

Output:

```python
RecommendationPackage
```

---

# Shared Data Models

Defined in:

```text
engineering_models.py
```

Includes:

```python
TelemetryFinding
DriverSetupAttribution
KnowledgePacket
RankedLever
SetupRecommendation
RecommendationPackage
CoachingInsight
```

---

# Example Integration

```python
from engineering_models import (
    TelemetryFinding
)

from manual_service import (
    SearchContext
)

from engineering_advisor import (
    advise
)

finding = TelemetryFinding(

    issue="entry understeer",

    confidence=0.91
)

context = SearchContext(

    vehicle="Porsche 963 GTP",

    manufacturer="Porsche",

    car_class="GTP"
)

package = advise(
    finding,
    context
)
```

Example result:

```text
Issue:
Entry Understeer

Vehicle:
Porsche 963 GTP

Recommendations:

1 Anti-Roll Bar
  Soften Front

2 Differential
  Reduce Locking

3 Differential Preload
  Decrease
```

---

# Design Principles

The system follows several engineering principles:

## Knowledge Driven

Manuals define:

```text
What adjustments affect behaviour
```

---

## Telemetry Driven

Telemetry defines:

```text
What behaviour is occurring
```

---

## Driver First

The system should determine:

```text
Driver issue?
```

before recommending:

```text
Setup change?
```

---

## Explainable

Recommendations should always include:

```text
Confidence
Reasoning
Supporting Evidence
```

---

# Current Capabilities

```text
✅ Manual ingestion
✅ Metadata generation
✅ Chunk generation
✅ Embeddings
✅ Semantic search
✅ Knowledge extraction
✅ Knowledge ranking
✅ Engineering reasoning
✅ Driver/setup attribution framework
✅ Engineering advisor API
```

---

# Future Roadmap

```text
⬜ Automatic telemetry issue detection
⬜ Driver coaching narrative generation
⬜ Telemetry evidence weighting
⬜ Track-specific reasoning
⬜ Vehicle-specific setup constraints
⬜ Shiftwright integration
```

---

# Version

```text
v0.1.0
```

---

# License

Internal Shiftwright development use.