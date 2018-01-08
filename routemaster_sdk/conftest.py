"""Global test setup and fixtures."""

import pytest
import requests

from routemaster_sdk import RoutemasterAPI

TEST_API_URL = 'http://localhost:2017'


@pytest.fixture()
def routemaster_api():
    """Create a ``RoutemasterAPI`` ready for testing."""
    return RoutemasterAPI(
        api_url=TEST_API_URL,
        session=requests.Session(),
    )
