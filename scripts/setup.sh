#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper Functions ---
echo_info() {
    echo "[INFO] $1"
}

echo_error() {
    echo "[ERROR] $1" >&2
    exit 1
}

# --- Prerequisite Checks ---
echo_info "Checking for prerequisites..."

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo_error "Docker is not installed. Please install it to continue."
    echo "Installation instructions: https://docs.docker.com/engine/install/"
    exit 1
fi
echo_info "Docker is installed."

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo_error "Docker Compose is not installed. Please install it to continue."
    echo "Installation instructions: https://docs.docker.com/compose/install/"
    exit 1
fi
echo_info "Docker Compose is installed."

# --- OS Detection and GitHub CLI Installation ---
echo_info "Detecting operating system..."
OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo_error "Unsupported operating system: $OSTYPE"
fi
echo_info "Operating System: $OS"

if ! command -v gh &> /dev/null; then
    echo_info "GitHub CLI (gh) not found. Installing..."
    if [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install gh -y
        elif command -v yum &> /dev/null; then
            sudo yum install -y gh
        else
            echo_error "Could not find apt-get or yum. Please install GitHub CLI manually."
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install gh
        else
            echo_error "Homebrew not found. Please install it to install GitHub CLI."
        fi
    fi
else
    echo_info "GitHub CLI (gh) is already installed."
fi

# --- Clone Azure REST API Specs ---
if [ ! -d "azure-rest-api-specs" ]; then
    echo_info "Cloning Azure REST API specifications..."
    gh repo clone Azure/azure-rest-api-specs
else
    echo_info "Azure REST API specifications directory already exists."
fi


# --- Python Virtual Environment Setup ---
echo_info "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo_info "Virtual environment created."
else
    echo_info "Virtual environment already exists."
fi

echo_info "Activating virtual environment and installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

echo_info "Setup complete. Virtual environment is ready and dependencies are installed."
echo_info "To activate the virtual environment, run: source .venv/bin/activate"
