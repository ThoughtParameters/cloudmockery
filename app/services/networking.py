"""
Dynamically generated API routes for the Azure Networking service.
"""
from typing import Any, Dict
from fastapi import APIRouter, Request

from app.openapi_parser import OpenAPIParser

# In-memory dictionary to simulate resource state.
in_memory_db: Dict[str, Any] = {}

router = APIRouter(
    prefix="/networking",
    tags=["networking"],
)

def _create_route_handler(parser: OpenAPIParser, endpoint_info: Dict[str, Any]):
    """
    Factory function to create a FastAPI route handler for a given endpoint.
    """
    async def route_handler(request: Request) -> Any:
        """
        Dynamically created route handler for a GET request.
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
    Parses the OpenAPI specs and dynamically creates routes for the networking service.
    """
    parser = OpenAPIParser(service_name="networking")
    endpoints = parser.parse()
    added_paths = set()

    for endpoint in endpoints:
        path = endpoint['path']
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
