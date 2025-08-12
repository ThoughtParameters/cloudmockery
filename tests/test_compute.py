"""
Basic tests for the dynamically generated compute service endpoints.
"""
import re
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _find_first_get_endpoint(prefix: str) -> str:
    """Finds the first registered GET endpoint with the given prefix."""
    for route in app.routes:
        if route.path.startswith(prefix) and "GET" in route.methods:
            return route.path
    return None

def _substitute_path_params(path: str) -> str:
    """Replaces path parameter placeholders with dummy string values."""
    return re.sub(r"\{(\w+)\}", r"test_\1", path)

def test_random_compute_get_endpoint():
    """
    Tests a dynamically generated GET endpoint for the compute service.

    It discovers a compute endpoint, sends a request to it, and asserts
    that the response is successful and contains data.
    """
    # Find a GET endpoint for the compute service to test
    endpoint_path = _find_first_get_endpoint("/compute")
    assert endpoint_path is not None, "No GET endpoints found for /compute to test."

    # Prepare the path by substituting any path parameters
    test_path = _substitute_path_params(endpoint_path)

    # Make the request
    response = client.get(test_path)

    # Assert the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data is not None
    assert isinstance(response_data, (dict, list))
    if isinstance(response_data, list):
        assert len(response_data) > 0
    else:
        assert len(response_data.keys()) > 0
