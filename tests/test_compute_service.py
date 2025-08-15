"""
Tests for the refactored, path-compliant compute service endpoints.
"""
from fastapi.testclient import TestClient
from typing import Dict

# All fixtures are provided by conftest.py

def test_vm_lifecycle(client: TestClient, auth_headers: Dict[str, str]):
    """
    Tests the full lifecycle of a virtual machine resource:
    PUT (create), GET (verify), GET (list), DELETE, GET (verify deletion).
    """
    subscription_id = "test-sub-123"
    resource_group_name = "test-rg-1"
    vm_name = "test-vm-01"

    # Define the API path
    api_path = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{vm_name}"

    # 1. Create the VM with PUT
    vm_payload = {
        "location": "eastus",
        "properties": {
            "hardwareProfile": {
                "vmSize": "Standard_D2_v2"
            }
        }
    }
    response_put = client.put(api_path, json=vm_payload, headers=auth_headers)
    assert response_put.status_code == 200
    created_data = response_put.json()
    assert created_data["name"] == vm_name
    assert created_data["resource_group"] == resource_group_name
    assert created_data["location"] == vm_payload["location"]
    assert "id" in created_data

    # 2. Retrieve the created VM with GET
    response_get = client.get(api_path, headers=auth_headers)
    assert response_get.status_code == 200
    assert response_get.json() == created_data

    # 3. List VMs in the resource group and find the new one
    list_path = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines"
    response_list = client.get(list_path, headers=auth_headers)
    assert response_list.status_code == 200
    vm_list = response_list.json()
    assert isinstance(vm_list, list)
    assert len(vm_list) > 0
    assert any(vm["name"] == vm_name for vm in vm_list)

    # 4. Delete the VM
    response_delete = client.delete(api_path, headers=auth_headers)
    assert response_delete.status_code == 204

    # 5. Verify the VM is gone (GET should now be 404)
    response_get_after_delete = client.get(api_path, headers=auth_headers)
    assert response_get_after_delete.status_code == 404
