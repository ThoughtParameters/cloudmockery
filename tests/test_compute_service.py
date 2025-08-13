"""
Tests for the database-driven compute service endpoints.
"""
from fastapi.testclient import TestClient

# The TestClient is now provided by the `client` fixture in conftest.py

def test_create_and_get_virtual_machine(client: TestClient):
    """
    Tests the full lifecycle of a virtual machine resource:
    1. Creates a new VM via a POST request.
    2. Verifies the creation response.
    3. Retrieves the same VM via a GET request using its ID.
    4. Verifies that the retrieved data matches the created data.
    """
    vm_payload = {
        "name": "test-vm-01",
        "resource_group": "test-rg",
        "location": "eastus",
        "vm_size": "Standard_D2s_v3",
        "provisioning_state": "Succeeded"
    }

    # Create the VM
    response_create = client.post("/compute/virtualmachines/", json=vm_payload)
    assert response_create.status_code == 200
    created_data = response_create.json()

    # Verify the created data
    assert "id" in created_data
    assert created_data["name"] == vm_payload["name"]
    assert created_data["resource_group"] == vm_payload["resource_group"]
    vm_id = created_data["id"]

    # Retrieve the VM by its ID
    response_get = client.get(f"/compute/virtualmachines/{vm_id}")
    assert response_get.status_code == 200
    retrieved_data = response_get.json()
    assert retrieved_data == created_data

def test_list_virtual_machines(client: TestClient):
    """
    Tests that the endpoint to list all VMs returns a list.
    This test relies on the state created by other tests, but fixtures
    isolate it. We'll create a VM first to test the list.
    """
    # Create a VM to ensure the list is not empty
    vm_payload = {"name": "test-vm-02", "resource_group": "test-rg-list", "location": "westus", "vm_size": "Standard_F4s"}
    client.post("/compute/virtualmachines/", json=vm_payload)

    response = client.get("/compute/virtualmachines/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(item["name"] == "test-vm-02" for item in data)

def test_get_nonexistent_virtual_machine(client: TestClient):
    """
    Tests that requesting a VM with an ID that does not exist
    returns a 404 Not Found error.
    """
    response = client.get("/compute/virtualmachines/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Virtual machine not found"}
