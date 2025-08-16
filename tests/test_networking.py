"""
Tests for the refactored, path-compliant networking service endpoints.
"""
from fastapi.testclient import TestClient
from typing import Dict

# All fixtures are provided by conftest.py

def test_vnet_lifecycle(client: TestClient, auth_headers: Dict[str, str]):
    """
    Tests the full lifecycle of a virtual network resource:
    PUT (create), GET (verify), GET (list), DELETE, GET (verify deletion).
    """
    subscription_id = "test-sub-123"
    resource_group_name = "test-rg-net-1"
    vnet_name = "test-vnet-01"

    # Define the API path for the specific VNet
    api_path = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{vnet_name}"

    # 1. Create the VNet with PUT
    vnet_payload = {
        "location": "westus",
        "properties": {
            "addressSpace": {
                "addressPrefixes": ["10.1.0.0/16"]
            }
        }
    }
    response_put = client.put(api_path, json=vnet_payload, headers=auth_headers)
    assert response_put.status_code == 200
    created_data = response_put.json()
    assert created_data["name"] == vnet_name
    assert created_data["resource_group"] == resource_group_name
    assert created_data["location"] == vnet_payload["location"]
    assert "id" in created_data

    # 2. Retrieve the created VNet with GET
    response_get = client.get(api_path, headers=auth_headers)
    assert response_get.status_code == 200
    assert response_get.json() == created_data

    # 3. List VNets in the resource group and find the new one
    list_path = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks"
    response_list = client.get(list_path, headers=auth_headers)
    assert response_list.status_code == 200
    vnet_list = response_list.json()
    assert isinstance(vnet_list, list)
    assert len(vnet_list) > 0
    assert any(vnet["name"] == vnet_name for vnet in vnet_list)

    # 4. Delete the VNet
    response_delete = client.delete(api_path, headers=auth_headers)
    assert response_delete.status_code == 204

    # 5. Verify the VNet is gone (GET should now be 404)
    response_get_after_delete = client.get(api_path, headers=auth_headers)
    assert response_get_after_delete.status_code == 404

def test_vnet_auth(client: TestClient):
    """
    Tests that unauthorized requests to the VNet endpoints are rejected.
    """
    api_path = "/subscriptions/test-sub-auth/resourceGroups/test-rg-auth/providers/Microsoft.Network/virtualNetworks/test-vnet-auth"
    vnet_payload = {
        "location": "westus",
        "properties": {"addressSpace": {"addressPrefixes": ["10.2.0.0/16"]}}
    }

    # Test PUT without auth
    response_no_auth = client.put(api_path, json=vnet_payload)
    assert response_no_auth.status_code == 401

    # Test GET with bad token
    response_bad_token = client.get(api_path, headers={"Authorization": "Bearer bad-token"})
    assert response_bad_token.status_code == 401
