"""
Parses Azure REST API OpenAPI specifications.

This module provides a class to parse OpenAPI specification files from the
'azure-rest-api-specs' repository. It extracts information about API endpoints,
focusing on GET requests, and can generate mock data from response schemas.
"""
import os
import json
from typing import List, Dict, Any, Set

from app.config import get_settings

class OpenAPIParser:
    """
    Parses Azure REST API OpenAPI specifications for a given service.

    This class is responsible for finding OpenAPI files within the azure-rest-api-specs
    directory, parsing them to extract endpoint information, and generating mock
    responses from JSON schemas.
    """

    def __init__(self, service_name: str):
        """
        Initializes the parser for a specific Azure service.

        Args:
            service_name: The name of the service (e.g., 'compute', 'storage').
        """
        settings = get_settings()
        # Handle service name mapping to directory name
        if service_name == 'networking':
            service_name = 'network'

        self.service_name = service_name
        self.service_spec_path = os.path.join(settings.API_SPECS_PATH, self.service_name)

    def _find_openapi_files(self) -> List[str]:
        """
        Finds all stable OpenAPI specification files for the service.

        It walks through the service's resource-manager directory and collects
        all .json files located under a 'stable' path.

        Returns:
            A list of absolute paths to the found OpenAPI JSON files.
        """
        openapi_files: Set[str] = set()
        resource_manager_path = os.path.join(self.service_spec_path, 'resource-manager')
        if not os.path.isdir(resource_manager_path):
            return []

        for root, _, files in os.walk(resource_manager_path):
            if 'stable' in root.split(os.sep):
                for filename in files:
                    if filename.endswith('.json'):
                        file_path = os.path.join(root, filename)
                        openapi_files.add(file_path)
        return list(openapi_files)

    def parse(self) -> List[Dict[str, Any]]:
        """
        Parses all found OpenAPI files and extracts GET endpoints.

        Returns:
            A list of dictionaries, each representing a GET endpoint with its
            path, operationId, and response schema.
        """
        endpoints: List[Dict[str, Any]] = []
        openapi_files = self._find_openapi_files()

        for file_path in openapi_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    spec = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

            if 'paths' not in spec or ('openapi' not in spec and 'swagger' not in spec):
                continue

            for path, path_item in spec.get('paths', {}).items():
                if 'get' in path_item:
                    get_op = path_item['get']
                    if get_op.get('deprecated'):
                        continue

                    response_200 = get_op.get('responses', {}).get('200', {})
                    if response_200:
                        schema = None
                        if 'openapi' in spec:  # OpenAPI 3
                            schema = response_200.get('content', {}).get('application/json', {}).get('schema')
                        elif 'swagger' in spec:  # OpenAPI 2
                            schema = response_200.get('schema')

                        if schema:
                            endpoints.append({
                                'path': path,
                                'operationId': get_op.get('operationId', f"get_{path.replace('/', '_')}"),
                                'response_schema': schema,
                                'spec': spec,
                            })
        return endpoints

    def generate_mock_data(self, schema: Dict[str, Any], spec: Dict[str, Any], visited_refs: Set[str] = None) -> Any:
        """
        Generates simple mock data from a JSON schema.

        This method handles basic data types, objects, arrays, and internal
        $ref references within the same specification file.

        Args:
            schema: The JSON schema to generate mock data from.
            spec: The full OpenAPI specification for resolving references.
            visited_refs: A set to track visited references to avoid recursion.

        Returns:
            Generated mock data that conforms to the schema.
        """
        if visited_refs is None:
            visited_refs = set()

        if '$ref' in schema:
            ref_path = schema['$ref']
            if ref_path in visited_refs:
                return f"recursive_ref_to_{ref_path}"

            visited_refs.add(ref_path)

            if ref_path.startswith('#/components/schemas/'):  # OpenAPI 3
                schema_name = ref_path.split('/')[-1]
                component_schema = spec.get('components', {}).get('schemas', {}).get(schema_name, {})
                return self.generate_mock_data(component_schema, spec, visited_refs)
            elif ref_path.startswith('#/definitions/'):  # OpenAPI 2
                schema_name = ref_path.split('/')[-1]
                component_schema = spec.get('definitions', {}).get(schema_name, {})
                return self.generate_mock_data(component_schema, spec, visited_refs)
            else:
                return {"unsupported_ref": ref_path}

        schema_type = schema.get('type')
        if schema_type == 'object':
            properties = schema.get('properties', {})
            if not properties:
                return {"key": "value"} # Handle free-form objects
            return {
                prop_name: self.generate_mock_data(prop_schema, spec, visited_refs)
                for prop_name, prop_schema in properties.items()
            }
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self.generate_mock_data(items_schema, spec, visited_refs)]
        elif schema_type == 'string':
            return schema.get('default', 'example_string')
        elif schema_type == 'integer':
            return schema.get('default', 123)
        elif schema_type == 'number':
            return schema.get('default', 123.45)
        elif schema_type == 'boolean':
            return schema.get('default', True)
        elif 'oneOf' in schema or 'anyOf' in schema:
            first_schema = schema.get('oneOf', [{}])[0] or schema.get('anyOf', [{}])[0]
            return self.generate_mock_data(first_schema, spec, visited_refs)
        elif 'properties' in schema:
            # If 'type' is missing but 'properties' exists, assume it's an object
            return {
                prop_name: self.generate_mock_data(prop_schema, spec, visited_refs)
                for prop_name, prop_schema in schema.get('properties', {}).items()
            }
        else:
            # For other cases (e.g., empty schema, unknown type), return an empty object
            # as a safe fallback instead of None.
            return {}
