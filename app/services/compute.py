"""
Dynamically generated API routes for the Azure Compute service.
"""
from typing import Any, Dict
from fastapi import APIRouter, Request

from app.openapi_parser import OpenAPIParser

# In-memory dictionary to simulate resource state.
# The key will be the request path, and the value will be the mock data.
in_memory_db: Dict[str, Any] = {}

router = APIRouter(
    prefix="/compute",
    tags=["compute"],
)

def _create_route_handler(parser: OpenAPIParser, endpoint_info: Dict[str, Any]):
    """
    Factory function to create a FastAPI route handler for a given endpoint.
    This closure ensures that each handler has the correct endpoint_info.
    """
    async def route_handler(request: Request) -> Any:
        """
        Dynamically created route handler for a GET request.

        This handler simulates state by using an in-memory dictionary. If a
        resource has been requested before, it returns the stored mock data.
        Otherwise, it generates, stores, and returns new mock data based on the
        OpenAPI response schema.
        """
        resource_key = request.url.path

        if resource_key not in in_memory_db:
            response_schema = endpoint_info['response_schema']
            spec = endpoint_info['spec']
            mock_data = parser.generate_mock_data(schema=response_schema, spec=spec)
            in_memory_db[resource_key] = mock_data

        return in_memory_db[resource_key]

    return route_handler

def _setup_routes():
    """
    Parses the OpenAPI specs and dynamically creates routes for the compute service.
    """
    parser = OpenAPIParser(service_name="compute")
    endpoints = parser.parse()
    added_paths = set()

    for endpoint in endpoints:
        path = endpoint['path']
        # Avoid adding duplicate routes for the same path, which can occur if the
        # path is defined in multiple spec files (e.g., different API versions).
        if path in added_paths:
            continue

        handler = _create_route_handler(parser, endpoint)

        router.add_api_route(
            path,
            handler,
            methods=["GET"],
            summary=endpoint.get('operationId', 'No summary available'),
            operation_id=endpoint.get('operationId')
        )
        added_paths.add(path)

# When this module is loaded, parse the specs and create the routes.
_setup_routes()
