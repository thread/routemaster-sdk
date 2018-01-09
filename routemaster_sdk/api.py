"""Python interface to the routemaster HTTP API."""

import urllib.parse
from typing import Any, Dict, List, NewType

import requests

from routemaster_sdk.types import (
    Label,
    State,
    LabelRef,
    Metadata,
    LabelName,
    StateMachine,
)
from routemaster_sdk.exceptions import (
    DeletedLabel,
    UnknownLabel,
    LabelAlreadyExists,
    UnknownStateMachine,
)

Json = NewType('Json', Dict[str, Any])


class RoutemasterAPI:
    """Wrapper around an instance of the routemaster HTTP API."""

    def __init__(self, api_url: str, session: requests.Session) -> None:
        """Create a new api wrapper around a given session and api base url."""
        self._api_url = api_url
        self._session = session

        self.delete = session.delete
        self.get = session.get
        self.patch = session.patch
        self.post = session.post

    def build_url(self, endpoint: str) -> str:
        """Build the url to the given endpoint for the wrapped API instance."""
        return urllib.parse.urljoin(self._api_url, endpoint)

    def build_label_url(self, label: LabelRef) -> str:
        """Build the url for a label in the wrapped API instance."""
        return self.build_url('state-machines/{0}/labels/{1}'.format(
            label.state_machine,
            label.name,
        ))

    def build_state_machine_url(self, state_machine: StateMachine) -> str:
        """Build the url for a state machine in the wrapped API instance."""
        return self.build_url(
            'state-machines/{0}/labels'.format(state_machine),
        )

    def get_status(self) -> Json:
        """Get the status of the wrapped API instance."""
        response = self.get(self.build_url(''))
        response.raise_for_status()
        return response.json()

    def get_state_machines(self) -> List[StateMachine]:
        """Get the state machines known to the wrapped API instance."""
        response = self.get(self.build_url('state-machines'))
        response.raise_for_status()

        return [
            StateMachine(data['name'])
            for data in response.json()['state-machines']
        ]

    def get_labels(self, state_machine: StateMachine) -> List[LabelRef]:
        """List the labels in the given state machine."""
        response = self.get(self.build_state_machine_url(state_machine))

        if response.status_code == 404:
            raise UnknownStateMachine(state_machine)

        response.raise_for_status()

        return [
            LabelRef(
                name=LabelName(data['name']),
                state_machine=state_machine,
            )
            for data in response.json()['labels']
        ]

    def get_label(self, label: LabelRef) -> Label:
        """
        Get a label within a given state machine.

        Errors:
        - ``UnknownLabel`` if the label is not known (HTTP 404).
        - ``DeletedLabel`` if the label has been deleted (HTTP 410).
        - ``requests.HTTPError`` for other HTTP errors.
        """

        response = self.get(self.build_label_url(label))

        if response.status_code == 404:
            raise UnknownLabel(label)
        elif response.status_code == 410:
            raise DeletedLabel(label)

        response.raise_for_status()

        data = response.json()

        return Label(
            ref=label,
            metadata=data['metadata'],
            state=State(data['state']),
        )

    def create_label(self, label: LabelRef, metadata: Metadata) -> Label:
        """
        Create a label with a given metadata, and start it in the state machine.

        Errors:
        - ``UnknownStateMachine`` if the state machine is not known (HTTP 404).
        - ``LabelAlreadyExists`` if the label already exists (HTTP 409).
        - ``requests.HTTPError`` for other HTTP errors.
        """
        response = self.post(
            self.build_label_url(label),
            json={'metadata': metadata},
        )

        if response.status_code == 404:
            raise UnknownStateMachine(label.state_machine)
        elif response.status_code == 409:
            raise LabelAlreadyExists(label)

        response.raise_for_status()

        data = response.json()

        return Label(
            ref=label,
            metadata=data['metadata'],
            state=State(data['state']),
        )

    def update_label(self, label: LabelRef, metadata: Metadata) -> Label:
        """
        Update a label in a state machine.

        Triggering progression if necessary according to the state machine
        configuration. Updates are _merged_ with existing metadata.

        Errors:
        - ``UnknownLabel`` if the label is not known (HTTP 404).
        - ``DeletedLabel`` if the label has been deleted (HTTP 410).
        - ``requests.HTTPError`` for other HTTP errors.
        """
        response = self.patch(
            self.build_label_url(label),
            json={'metadata': metadata},
        )

        if response.status_code == 404:
            raise UnknownLabel(label)
        elif response.status_code == 410:
            raise DeletedLabel(label)

        response.raise_for_status()

        data = response.json()

        return Label(
            ref=label,
            metadata=data['metadata'],
            state=State(data['state']),
        )

    def delete_label(self, label: LabelRef) -> None:
        """
        Delete a label in a state machine.

        Marks a label as deleted, but does not remove it from the database.
        Deleted labels cannot be updated and will not move state.

        Errors:
        - ``UnknownStateMachine`` if the state machine is not known (HTTP 404).
        - ``requests.HTTPError`` for other HTTP errors.
        """
        response = self.delete(self.build_label_url(label))

        if response.status_code == 404:
            raise UnknownStateMachine(label.state_machine)

        response.raise_for_status()
