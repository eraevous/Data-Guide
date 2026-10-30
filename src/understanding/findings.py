"""Typed findings: the unit of understanding (requirement A)."""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Kind = Literal["observation", "interpretation", "hypothesis", "action", "question"]
Generator = Literal["rule", "human"]

KINDS: tuple[str, ...] = ("observation", "interpretation", "hypothesis", "action", "question")

# What each kind may claim. The report shows these alongside every finding.
CONFIDENCE_MEANING = {
    "measured": "a reproducible calculation on this data; says nothing about why",
    "untested": "a possible explanation nobody has checked",
    "stated": "written by a person in the annotations; provenance, not proof",
    "low": "rule-based reading with weak support", "medium": "rule-based reading with moderate support",
    "high": "rule-based reading with strong support", "n/a": "not applicable",
}

KIND_MEANING = {
    "observation": "measured directly from this data",
    "interpretation": "a reading of an observation; may be wrong",
    "hypothesis": "a possible explanation to test, not established",
    "action": "a suggested next step for the analyst to judge",
    "question": "something this data cannot answer; needs a person",
}


@dataclass
class Finding:
    kind: Kind
    rule: str
    statement: str
    subjects: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    confidence: Literal["high", "medium", "low"] = "medium"
    generator: Generator = "rule"
    based_on: list[str] = field(default_factory=list)
    relevance: str | None = None

    @property
    def id(self) -> str:
        key = "|".join([self.kind, self.rule, ",".join(sorted(self.subjects)), self.generator])
        if self.generator == "human":
            key += "|" + self.statement
        return f"F-{hashlib.sha256(key.encode()).hexdigest()[:10]}"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["id"] = self.id
        # A measurement and an explanation carry different obligations, so their "confidence"
        # means different things and is labelled per kind.
        if self.generator == "human":
            d["confidence"] = "stated"
        elif self.kind == "observation":
            d["confidence"] = "measured"
        elif self.kind == "hypothesis":
            d["confidence"] = "untested"
        elif self.kind == "question":
            d["confidence"] = "n/a"
        return d


def sort_findings(findings: list[Finding]) -> list[Finding]:
    order = {k: i for i, k in enumerate(KINDS)}
    rank = {"target": 0, "question": 1, None: 2}
    return sorted(findings, key=lambda f: (order[f.kind], rank.get(f.relevance, 2), f.rule,
                                           ",".join(f.subjects), f.statement))
