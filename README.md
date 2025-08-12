# Azure Emulator

This project provides a mock server for the Azure REST API, intended for local development and testing purposes. It uses FastAPI to create a lightweight and fast emulator that can be run locally or in a container.

## Getting Started

1.  **Run the setup script:**
    ```bash
    bash scripts/setup.sh
    ```
2.  **Start the server:**
    ```bash
    docker-compose up
    ```

The API will be available at `http://localhost:8000`.