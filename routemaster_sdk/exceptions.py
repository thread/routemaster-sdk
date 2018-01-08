"""Well known exceptions."""


class UnknownLabel(ValueError):
    """Represents a label unknown in the given state machine."""
    deleted = False

    def __init__(self, label):
        self.label = label

    def __str__(self):
        return "{0}: {1}".format(self.__class__.__name__, self.label)


class DeletedLabel(UnknownLabel):
    """Represents a label deleted in the given state machine."""
    deleted = True


class UnknownStateMachine(ValueError):
    """Represents a state machine not in the system."""

    def __init__(self, state_machine):
        self.state_machine = state_machine

    def __str__(self):
        return "{0}: {1}".format(self.__class__.__name__, self.state_machine)


class LabelAlreadyExists(ValueError):
    """Thrown when a label already exists in the state machine."""

    def __init__(self, label):
        self.label = label

    def __str__(self):
        return "{0}: {1}".format(self.__class__.__name__, self.label)
