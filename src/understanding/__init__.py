"""Understanding layer: typed findings, inferred semantics, and an explicit register of unknowns.

Data Guide's recovered vision asks for *understanding before modeling*: assumptions,
data-generating process, EDA, usefulness. This package turns a DataFrame (plus optional
human annotations) into a versioned, machine-readable artifact. Reports are derived views of it.

Findings are typed (observation, interpretation, hypothesis, action, question). Each one carries
evidence and names its generator (``rule`` or ``human``). Inferred semantics stay labelled as
inferred until a human states otherwise. What the table cannot tell us is kept in the
assumptions/data-generating-process register as open questions; it is never guessed.
"""
from understanding.artifact import SCHEMA, build_artifact
from understanding.compare import compare_artifacts

__all__ = ["SCHEMA", "build_artifact", "compare_artifacts"]
