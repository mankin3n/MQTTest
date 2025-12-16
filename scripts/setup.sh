#!/bin/bash
# Setup script for the test framework

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_header() {
    echo ""
    echo "============================================"
    echo "$1"
    echo "============================================"
}

print_success() {
    echo "✓ $1"
}

print_error() {
    echo "✗ $1" >&2
}

# Check Python version
check_python() {
    print_header "Checking Python version"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_header "Setting up virtual environment"
    cd "$PROJECT_ROOT"

    if [ -d "venv" ]; then
        print_success "Virtual environment already exists"
    else
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
}

# Install dependencies
install_deps() {
    print_header "Installing dependencies"
    cd "$PROJECT_ROOT"

    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Generate certificates
generate_certs() {
    print_header "Generating certificates"
    cd "$PROJECT_ROOT"

    source venv/bin/activate
    python3 scripts/generate_certs.py
    print_success "Certificates generated"
}

# Create necessary directories
create_dirs() {
    print_header "Creating directories"
    cd "$PROJECT_ROOT"

    mkdir -p reports logs data
    print_success "Directories created"
}

# Main setup
main() {
    print_header "SmartHome IoT Test Framework Setup"

    check_python
    create_venv
    install_deps
    create_dirs
    generate_certs

    print_header "Setup completed successfully!"
    echo ""
    echo "To activate the virtual environment, run:"
    echo "  source venv/bin/activate"
    echo ""
    echo "To run tests, use the CLI:"
    echo "  python3 cli.py run --suite smoke"
    echo ""
    echo "For more information, see the README.md"
    echo ""
}

main
