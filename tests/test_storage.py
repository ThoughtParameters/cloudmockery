"""
Tests for the database-driven storage service endpoints.
"""
from fastapi.testclient import TestClient
from typing import Dict

# All fixtures are provided by conftest.py

def test_storage_account_lifecycle(client: TestClient, auth_headers: Dict[str, str]):
    """
    Tests the full lifecycle of a storage account resource.
    """
    subscription_id = "test-sub-123"
    resource_group_name = "test-rg-sa-1"
    account_name = "teststorageaccount01"

    api_path = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/storageAccounts/{account_name}"

    # 1. Create the Storage Account with PUT
    sa_payload = {
        "location": "eastus",
        "sku": {"name": "Standard_LRS"},
        "kind": "StorageV2"
    }
    response_put = client.put(api_path, json=sa_payload, headers=auth_headers)
    # Azure returns 200 for update, 202 for create (accepted), 201 for create immediate
    # For a simple mock, we'll just accept 200 for upsert
    assert response_put.status_code == 200
    created_data = response_put.json()
    assert created_data["name"] == account_name
    assert created_data["resource_group"] == resource_group_name
    assert "id" in created_data

    # 2. Retrieve the created Storage Account with GET
    response_get = client.get(api_path, headers=auth_headers)
    assert response_get.status_code == 200
    assert response_get.json() == created_data

    # 3. List Storage Accounts in the resource group
    list_path = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/storageAccounts"
    response_list = client.get(list_path, headers=auth_headers)
    assert response_list.status_code == 200
    sa_list = response_list.json()
    assert isinstance(sa_list, list)
    assert any(sa["name"] == account_name for sa in sa_list)

    # 4. Delete the Storage Account
    response_delete = client.delete(api_path, headers=auth_headers)
    assert response_delete.status_code == 204

    # 5. Verify the Storage Account is gone
    response_get_after_delete = client.get(api_path, headers=auth_headers)
    assert response_get_after_delete.status_code == 404

def test_storage_account_auth(client: TestClient):
    """
    Tests that unauthorized requests to the Storage Account endpoints are rejected.
    """
    api_path = "/subscriptions/test-sub-auth/resourceGroups/test-rg-auth/providers/Microsoft.Storage/storageAccounts/testsaauth"
    sa_payload = {
        "location": "eastus",
        "sku": {"name": "Standard_LRS"},
        "kind": "StorageV2"
    }

    # Test PUT without auth
    response_no_auth = client.put(api_path, json=sa_payload)
    assert response_no_auth.status_code == 401

    # Test GET with bad token
    response_bad_token = client.get(api_path, headers={"Authorization": "Bearer bad-token"})
    assert response_bad_token.status_code == 401
