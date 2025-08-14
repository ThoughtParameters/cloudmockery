"""
Tests for the database-driven networking service endpoints.
"""
from fastapi.testclient import TestClient
from typing import Dict

# All fixtures are provided by conftest.py

def test_create_and_get_vnet(client: TestClient, auth_headers: Dict[str, str]):
    """
    Tests creating a virtual network and then retrieving it.
    """
    vnet_payload = {
        "name": "test-vnet-01",
        "resource_group": "test-rg-1",
        "location": "eastus",
        "address_space": "10.0.0.0/16",
    }

    # Create the VNet
    response_create = client.post(
        "/networking/virtualnetworks/", json=vnet_payload, headers=auth_headers
    )
    assert response_create.status_code == 200
    created_data = response_create.json()

    # Verify the created data
    assert "id" in created_data
    assert created_data["name"] == vnet_payload["name"]
    vnet_id = created_data["id"]

    # Retrieve the VNet by its ID
    response_get = client.get(f"/networking/virtualnetworks/{vnet_id}", headers=auth_headers)
    assert response_get.status_code == 200
    assert response_get.json() == created_data

def test_list_vnets(client: TestClient, auth_headers: Dict[str, str]):
    """
    Tests listing virtual networks after creating one.
    """
    # Create a VNet to ensure the list is not empty
    vnet_payload = {
        "name": "test-vnet-02",
        "resource_group": "test-rg-2",
        "location": "westus",
        "address_space": "192.168.0.0/16",
    }
    client.post("/networking/virtualnetworks/", json=vnet_payload, headers=auth_headers)

    response = client.get("/networking/virtualnetworks/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(item["name"] == "test-vnet-02" for item in data)

def test_get_nonexistent_vnet(client: TestClient, auth_headers: Dict[str, str]):
    """
    Tests that requesting a VNet with an ID that does not exist
    returns a 404 Not Found error.
    """
    response = client.get("/networking/virtualnetworks/99999", headers=auth_headers)
    assert response.status_code == 404

def test_create_vnet_unauthorized(client: TestClient):
    """
    Tests that creating a VNet without an auth token fails with a 401 error.
    """
    vnet_payload = {
        "name": "unauth-vnet",
        "resource_group": "unauth-rg",
        "location": "eastus",
        "address_space": "172.16.0.0/16",
    }
    response = client.post("/networking/virtualnetworks/", json=vnet_payload)  # No headers
    assert response.status_code == 401
