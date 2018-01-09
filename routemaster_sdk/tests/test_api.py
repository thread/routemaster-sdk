import json

import pytest
import requests
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
def test_get_status_error_response(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.GET,
        'http://localhost:2017/',
        body=json.dumps({
            'status': 'error',
            'message': 'Cannot connect to database',
        }),
        content_type='application/json',
        status=503,
    )

    with pytest.raises(requests.HTTPError):
        routemaster_api.get_status()


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
def test_get_state_machines_error_response(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.GET,
        'http://localhost:2017/state-machines',
        content_type='application/json',
        status=502,
    )

    with pytest.raises(requests.HTTPError):
        routemaster_api.get_state_machines()


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


@httpretty.activate
def test_get_labels_error_response(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.GET,
        'http://localhost:2017/state-machines/none/labels',
        content_type='application/json',
        status=502,
    )

    testing_machine = StateMachine('none')

    with pytest.raises(requests.HTTPError):
        routemaster_api.get_labels(testing_machine)


@httpretty.activate
def test_create_label(routemaster_api: RoutemasterAPI):
    expected_sent = {'foo': 'sent'}
    expected_returned = {'foo': 'returned'}

    httpretty.register_uri(
        httpretty.POST,
        'http://localhost:2017/state-machines/testing-machine/labels/demo-label',
        body=json.dumps({
            'metadata': expected_returned,
            'state': 'first-state',
        }),
        content_type='application/json',
        status=201,
    )

    label_ref = LabelRef(
        LabelName('demo-label'),
        StateMachine('testing-machine'),
    )

    returned_label = routemaster_api.create_label(
        label_ref,
        metadata=expected_sent,
    )

    assert returned_label == Label(
        label_ref,
        expected_returned,
        State('first-state'),
    )

    last_request = httpretty.last_request()
    sent_data = json.loads(last_request.body.decode('utf-8'))
    assert sent_data == {'metadata': expected_sent}


@httpretty.activate
def test_create_label_error_response(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.POST,
        'http://localhost:2017/state-machines/testing-machine/labels/demo-label',
        content_type='application/json',
        status=502,
    )

    label_ref = LabelRef(
        LabelName('demo-label'),
        StateMachine('testing-machine'),
    )

    with pytest.raises(requests.HTTPError):
        routemaster_api.create_label(label_ref, metadata={})


@httpretty.activate
def test_create_label_unknown_state_machine(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.POST,
        'http://localhost:2017/state-machines/none/labels/demo-label',
        content_type='application/json',
        status=404,
    )

    testing_machine = StateMachine('none')
    label_ref = LabelRef(LabelName('demo-label'), testing_machine)

    with pytest.raises(UnknownStateMachine) as e:
        routemaster_api.create_label(label_ref, metadata={})

    assert e.value.state_machine == 'none'


@httpretty.activate
def test_create_label_already_exists(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.POST,
        'http://localhost:2017/state-machines/testing-machine/labels/demo-label',
        content_type='application/json',
        status=409,
    )

    label_ref = LabelRef(
        LabelName('demo-label'),
        StateMachine('testing-machine'),
    )

    with pytest.raises(LabelAlreadyExists) as e:
        routemaster_api.create_label(label_ref, metadata={})

    assert e.value.label == label_ref


@httpretty.activate
def test_update_label(routemaster_api: RoutemasterAPI):
    expected_sent = {'foo': 'sent'}
    expected_returned = {'foo': 'returned'}

    httpretty.register_uri(
        httpretty.PATCH,
        'http://localhost:2017/state-machines/testing-machine/labels/demo-label',
        body=json.dumps({
            'metadata': expected_returned,
            'state': 'first-state',
        }),
        content_type='application/json',
    )

    label_ref = LabelRef(
        LabelName('demo-label'),
        StateMachine('testing-machine'),
    )

    returned_label = routemaster_api.update_label(
        label_ref,
        metadata=expected_sent,
    )

    assert returned_label == Label(
        label_ref,
        expected_returned,
        State('first-state'),
    )

    last_request = httpretty.last_request()
    sent_data = json.loads(last_request.body.decode('utf-8'))
    assert sent_data == {'metadata': expected_sent}


@httpretty.activate
def test_update_label_error_response(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.PATCH,
        'http://localhost:2017/state-machines/testing-machine/labels/demo-label',
        content_type='application/json',
        status=502,
    )

    label_ref = LabelRef(
        LabelName('demo-label'),
        StateMachine('testing-machine'),
    )

    with pytest.raises(requests.HTTPError):
        routemaster_api.update_label(label_ref, metadata={})


@httpretty.activate
def test_update_label_unknown_label(routemaster_api: RoutemasterAPI):
    # Note: the update API doesn't differentiate between an unknown label and an
    # unknown state machine.
    httpretty.register_uri(
        httpretty.PATCH,
        'http://localhost:2017/state-machines/testing-machine/labels/none',
        content_type='application/json',
        status=404,
    )

    label_ref = LabelRef(
        LabelName('none'),
        StateMachine('testing-machine'),
    )

    with pytest.raises(UnknownLabel) as e:
        routemaster_api.update_label(label_ref, metadata={})

    assert e.value.label == label_ref


@httpretty.activate
def test_update_label_deleted_label(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.PATCH,
        'http://localhost:2017/state-machines/testing-machine/labels/was-deleted',
        content_type='application/json',
        status=410,
    )

    label_ref = LabelRef(
        LabelName('was-deleted'),
        StateMachine('testing-machine'),
    )

    with pytest.raises(DeletedLabel) as e:
        routemaster_api.update_label(label_ref, metadata={})

    assert e.value.label == label_ref


@httpretty.activate
def test_delete_label(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.DELETE,
        'http://localhost:2017/state-machines/testing-machine/labels/demo-label',
        content_type='application/json',
        status=204,
    )

    label_ref = LabelRef(
        LabelName('demo-label'),
        StateMachine('testing-machine'),
    )

    routemaster_api.delete_label(label_ref)


@httpretty.activate
def test_delete_label_error_response(routemaster_api: RoutemasterAPI):
    httpretty.register_uri(
        httpretty.DELETE,
        'http://localhost:2017/state-machines/testing-machine/labels/demo-label',
        content_type='application/json',
        status=502,
    )

    label_ref = LabelRef(
        LabelName('demo-label'),
        StateMachine('testing-machine'),
    )

    with pytest.raises(requests.HTTPError):
        routemaster_api.delete_label(label_ref)


@httpretty.activate
def test_delete_label_unknown_state_machine(routemaster_api: RoutemasterAPI):
    # Note: the update API doesn't differentiate between an unknown label and an
    # unknown state machine.
    httpretty.register_uri(
        httpretty.DELETE,
        'http://localhost:2017/state-machines/none/labels/demo-label',
        content_type='application/json',
        status=404,
    )

    testing_machine = StateMachine('none')
    label_ref = LabelRef(LabelName('demo-label'), testing_machine)

    with pytest.raises(UnknownStateMachine) as e:
        routemaster_api.delete_label(label_ref)

    assert e.value.state_machine == 'none'
