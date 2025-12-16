#!/bin/bash
# Certificate management helper script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CERTS_DIR="$PROJECT_ROOT/certs"

print_header() {
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

generate_all() {
    print_header "Generating all certificates"
    cd "$PROJECT_ROOT"
    python3 scripts/generate_certs.py
}

clean_all() {
    print_header "Cleaning all certificates"
    if [ -d "$CERTS_DIR" ]; then
        rm -rf "$CERTS_DIR"/{ca,broker,devices,clients}/*
        print_success "All certificates removed"
    else
        print_error "Certs directory not found"
    fi
}

verify_cert() {
    local cert_path="$1"
    print_header "Verifying certificate: $cert_path"

    if [ ! -f "$cert_path" ]; then
        print_error "Certificate not found: $cert_path"
        return 1
    fi

    openssl x509 -in "$cert_path" -text -noout
}

list_certs() {
    print_header "Certificate inventory"

    echo -e "\n[CA Certificates]"
    if [ -d "$CERTS_DIR/ca" ]; then
        ls -lh "$CERTS_DIR/ca/"*.crt 2>/dev/null || echo "  No CA certificates found"
    fi

    echo -e "\n[Broker Certificates]"
    if [ -d "$CERTS_DIR/broker" ]; then
        ls -lh "$CERTS_DIR/broker/"*.crt 2>/dev/null || echo "  No broker certificates found"
    fi

    echo -e "\n[Device Certificates]"
    if [ -d "$CERTS_DIR/devices" ]; then
        ls -lh "$CERTS_DIR/devices/"*.crt 2>/dev/null || echo "  No device certificates found"
    fi

    echo -e "\n[Client Certificates]"
    if [ -d "$CERTS_DIR/clients" ]; then
        ls -lh "$CERTS_DIR/clients/"*.crt 2>/dev/null || echo "  No client certificates found"
    fi
}

check_expiry() {
    print_header "Checking certificate expiry dates"

    for cert in "$CERTS_DIR"/*/*.crt; do
        if [ -f "$cert" ]; then
            echo -e "\n$(basename $cert):"
            openssl x509 -in "$cert" -noout -dates | grep -E "notBefore|notAfter"
        fi
    done
}

show_help() {
    cat << EOF
Certificate Manager - SmartHome IoT Test Platform

Usage: $0 [COMMAND]

Commands:
    generate    Generate all certificates (CA, broker, devices, clients)
    clean       Remove all generated certificates
    list        List all certificates
    verify      Verify a specific certificate
    expiry      Check expiry dates of all certificates
    help        Show this help message

Examples:
    $0 generate
    $0 list
    $0 verify certs/ca/ca.crt
    $0 expiry

EOF
}

# Main script logic
case "${1:-help}" in
    generate)
        generate_all
        ;;
    clean)
        clean_all
        ;;
    list)
        list_certs
        ;;
    verify)
        if [ -z "$2" ]; then
            print_error "Please specify a certificate path"
            exit 1
        fi
        verify_cert "$2"
        ;;
    expiry)
        check_expiry
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
