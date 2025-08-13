# Azure Emulator

[![CI](https://github.com/thought-parameters-llc/cloudmockery/actions/workflows/ci.yml/badge.svg)](https://github.com/thought-parameters-llc/cloudmockery/actions/workflows/ci.yml)

An open-source emulator for the Azure REST API, designed for local development, testing, and CI/CD environments. This project provides a mock server that dynamically generates API endpoints based on the official Azure OpenAPI specifications, allowing you to test your infrastructure-as-code (IaC) tools like Terraform and OpenTofu without needing a live Azure subscription.

## Features

- **Dynamic API Generation**: Automatically creates mock API endpoints from the official [Azure REST API Specs](https://github.com/Azure/azure-rest-api-specs).
- **Database Persistence**: Uses a PostgreSQL backend to store the state of created resources, ensuring data persists across API calls.
- **Terraform/OpenTofu Compatible**: Designed to work as a local backend for testing Azure provider configurations.
- **Containerized**: Runs in Docker, making setup and integration simple and consistent.
- **Extensible**: Built with FastAPI and SQLModel, providing a modern, high-performance foundation for adding new services and features.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   Docker and Docker Compose
-   Git
-   Python 3.11+
-   The GitHub CLI (`gh`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/thought-parameters-llc/cloudmockery.git
    cd cloudmockery
    ```

2.  **Run the setup script:**
    This script will clone the required Azure API specifications repository and set up a Python virtual environment.
    ```bash
    bash scripts/setup.sh
    ```

3.  **Start the services:**
    This command will build the Docker containers and start the FastAPI application and the PostgreSQL database.
    ```bash
    docker-compose up --build
    ```

The API will now be available at `http://localhost:8000`. You can view the auto-generated API documentation at `http://localhost:8000/docs`.

## Usage

The emulator works by creating mock resources that are stored in its database. You can interact with it using any HTTP client, such as `curl` or Postman, or by configuring your IaC tool to point to the local emulator endpoint.

**Example: Creating a Virtual Machine**

```bash
curl -X 'POST' \
  'http://localhost:8000/compute/virtualmachines/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "test-vm-from-curl",
    "resource_group": "my-test-rg",
    "location": "eastus",
    "vm_size": "Standard_DS1_v2"
  }'
```

## Docker

You can build and run the Docker image manually without using Docker Compose.

**Build the image:**
```bash
docker build -t azure-emulator .
```

**Run the container:**
Note: This method requires a running PostgreSQL instance and the necessary environment variables to be passed to the container. Using the provided `docker-compose.yml` is the recommended approach for local development.

## Automation & Workflows

This project uses GitHub Actions for CI/CD automation.

### CI Workflow (`ci.yml`)

-   **Trigger**: Runs on every `push` to the `main` branch and on all `pull_request` events.
-   **Jobs**:
    -   `lint_and_test`: Installs dependencies, runs linters (placeholder), and executes the `pytest` test suite to ensure code quality and correctness.

### Docker Publishing Workflow (`docker-publish.yml`)

-   **Trigger**: Runs automatically when a new version tag (e.g., `v1.0.0`) is pushed to the repository.
-   **Jobs**:
    -   `build-and-publish`: Builds a multi-platform Docker image and publishes it to the GitHub Container Registry (GHCR).

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

### Development Process

1.  **Fork the Project**: Click the 'Fork' button at the top right of this page.
2.  **Clone your Fork**: `git clone https://github.com/YOUR_USERNAME/cloudmockery.git`
3.  **Create your Feature Branch**: `git checkout -b feature/AmazingFeature`
4.  **Make your Changes**: Implement your new feature or bug fix.
5.  **Run Tests**: Make sure the test suite passes with your changes: `pytest`
6.  **Commit your Changes**: `git commit -m 'Add some AmazingFeature'`
7.  **Push to the Branch**: `git push origin feature/AmazingFeature`
8.  **Open a Pull Request**: Go to the original repository and open a new pull request.

## License

Distributed under the MIT License. See `LICENSE` for more information.