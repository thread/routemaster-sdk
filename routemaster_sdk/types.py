"""Types to match those in the API."""

from typing import Any, Dict, NewType, NamedTuple

LabelName = NewType('LabelName', str)
StateMachine = NewType('StateMachine', str)
State = NewType('State', str)

Metadata = Dict[str, Any]

LabelRef = NamedTuple('LabelRef', [
    ('name', LabelName),
    ('state_machine', StateMachine),
])

Label = NamedTuple('Label', [
    ('ref', LabelRef),
    ('metadata', Metadata),
    ('state', State),
])
