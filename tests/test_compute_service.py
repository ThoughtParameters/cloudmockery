"""
Tests for the database-driven compute service endpoints, including auth.
"""
from fastapi.testclient import TestClient
from typing import Dict

# All fixtures are provided by conftest.py

def test_create_vm(client: TestClient, auth_headers: Dict[str, str]):
    """Tests successful VM creation with valid authentication."""
    vm_payload = {
        "name": "test-vm-01",
        "resource_group": "test-rg-1",
        "location": "eastus",
        "vm_size": "Standard_D2s_v3",
    }
    response = client.post("/compute/virtualmachines/", json=vm_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == vm_payload["name"]
    assert "id" in data

def test_get_created_vm(client: TestClient, auth_headers: Dict[str, str]):
    """Tests retrieving a specific VM after creating it."""
    vm_payload = {
        "name": "test-vm-02",
        "resource_group": "test-rg-2",
        "location": "westus",
        "vm_size": "Standard_F4s",
    }
    response_create = client.post("/compute/virtualmachines/", json=vm_payload, headers=auth_headers)
    assert response_create.status_code == 200
    created_data = response_create.json()
    vm_id = created_data["id"]

    response_get = client.get(f"/compute/virtualmachines/{vm_id}", headers=auth_headers)
    assert response_get.status_code == 200
    assert response_get.json() == created_data

def test_list_vms(client: TestClient, auth_headers: Dict[str, str]):
    """Tests listing all VMs after creating one."""
    response = client.get("/compute/virtualmachines/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_nonexistent_vm(client: TestClient, auth_headers: Dict[str, str]):
    """Tests that requesting a non-existent VM returns a 404 Not Found error."""
    response = client.get("/compute/virtualmachines/99999", headers=auth_headers)
    assert response.status_code == 404

def test_create_vm_unauthorized(client: TestClient):
    """Tests that creating a VM without an auth token fails with a 401 error."""
    vm_payload = {"name": "test-vm-03", "resource_group": "test-rg-3", "location": "eastus", "vm_size": "Standard_D2s_v3"}
    response = client.post("/compute/virtualmachines/", json=vm_payload)  # No headers
    assert response.status_code == 401

def test_create_vm_bad_token(client: TestClient):
    """Tests that creating a VM with an invalid auth token fails with a 401 error."""
    vm_payload = {"name": "test-vm-04", "resource_group": "test-rg-4", "location": "eastus", "vm_size": "Standard_D2s_v3"}
    response = client.post(
        "/compute/virtualmachines/",
        json=vm_payload,
        headers={"Authorization": "Bearer bad-token"},
    )
    assert response.status_code == 401
