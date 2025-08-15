"""
Tests for the database-driven storage service endpoints.
"""
from fastapi.testclient import TestClient
from typing import Dict

# All fixtures are provided by conftest.py

def test_create_and_get_storage_account(client: TestClient, auth_headers: Dict[str, str]):
    """
    Tests creating a storage account and then retrieving it.
    """
    account_payload = {
        "name": "teststorageaccount01",
        "resource_group": "test-rg-1",
        "location": "eastus",
        "sku": "Standard_LRS",
        "kind": "StorageV2",
    }

    # Create the Storage Account
    response_create = client.post(
        "/storage/storageaccounts/", json=account_payload, headers=auth_headers
    )
    assert response_create.status_code == 200
    created_data = response_create.json()

    # Verify the created data
    assert "id" in created_data
    assert created_data["name"] == account_payload["name"]
    account_id = created_data["id"]

    # Retrieve the Storage Account by its ID
    response_get = client.get(f"/storage/storageaccounts/{account_id}", headers=auth_headers)
    assert response_get.status_code == 200
    assert response_get.json() == created_data

def test_list_storage_accounts(client: TestClient, auth_headers: Dict[str, str]):
    """
    Tests listing storage accounts after creating one.
    """
    # Create a storage account to ensure the list is not empty
    account_payload = {
        "name": "teststorageaccount02",
        "resource_group": "test-rg-2",
        "location": "westus",
        "sku": "Premium_LRS",
        "kind": "BlockBlobStorage",
    }
    client.post("/storage/storageaccounts/", json=account_payload, headers=auth_headers)

    response = client.get("/storage/storageaccounts/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(item["name"] == "teststorageaccount02" for item in data)

def test_get_nonexistent_storage_account(client: TestClient, auth_headers: Dict[str, str]):
    """
    Tests that requesting a storage account with an ID that does not exist
    returns a 404 Not Found error.
    """
    response = client.get("/storage/storageaccounts/99999", headers=auth_headers)
    assert response.status_code == 404

def test_create_storage_account_unauthorized(client: TestClient):
    """
    Tests that creating a storage account without an auth token fails with a 401 error.
    """
    account_payload = {
        "name": "unauthstorage",
        "resource_group": "unauth-rg",
        "location": "eastus",
        "sku": "Standard_LRS",
        "kind": "StorageV2",
    }
    response = client.post("/storage/storageaccounts/", json=account_payload)  # No headers
    assert response.status_code == 401
