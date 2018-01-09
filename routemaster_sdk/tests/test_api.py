import json

import pytest
import httpretty

from routemaster_sdk import (
    Label,
    State,
    LabelRef,
    LabelName,
    DeletedLabel,
    StateMachine,
    UnknownLabel,
    RoutemasterAPI,
    LabelAlreadyExists,
    UnknownStateMachine,
)


@httpretty.activate
def test_get_status(routemaster_api: RoutemasterAPI):
    expected = {'status': 'ok', 'state-machines': '/state-machines'}

    httpretty.register_uri(
        httpretty.GET,
        'http://localhost:2017/',
        body=json.dumps(expected),
        content_type='application/json',
    )

    response_json = routemaster_api.get_status()

    assert response_json == expected


@httpretty.activate
def test_get_state_machines(routemaster_api: RoutemasterAPI):
    data = {'state-machines': [
        {
            'name': 'testing-machine',
            'labels': '/state-machines/testing-machine/labels',
        }
    ]}

    httpretty.register_uri(
        httpretty.GET,
        'http://localhost:2017/state-machines',
        body=json.dumps(data),
        content_type='application/json',
    )

    response_json = routemaster_api.get_state_machines()

    assert response_json == [StateMachine('testing-machine')]


@httpretty.activate
def test_get_labels(routemaster_api: RoutemasterAPI):
    data = {'labels': [
        {'name': 'first-label'},
        {'name': 'other-label'},
    ]}

    httpretty.register_uri(
        httpretty.GET,
        'http://localhost:2017/state-machines/testing-machine/labels',
        body=json.dumps(data),
        content_type='application/json',
    )

    testing_machine = StateMachine('testing-machine')

    labels = routemaster_api.get_labels(testing_machine)

    assert labels == [
        LabelRef(LabelName('first-label'), testing_machine),
        LabelRef(LabelName('other-label'), testing_machine),
    ]


@httpretty.activate
def test_get_labels_unknown_state_machine(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.GET,
        'http://localhost:2017/state-machines/none/labels',
        content_type='application/json',
        status=404,
    )

    testing_machine = StateMachine('none')

    with pytest.raises(UnknownStateMachine) as e:
        routemaster_api.get_labels(testing_machine)

    assert e.value.state_machine == 'none'
