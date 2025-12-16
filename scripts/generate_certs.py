#!/usr/bin/env python3
"""
Certificate generation script for IoT platform testing.
Creates CA, broker, device, and client certificates for mTLS authentication.
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class CertificateAuthority:
    """Certificate Authority for generating and signing certificates."""

    def __init__(self, certs_dir='certs'):
        self.certs_dir = Path(certs_dir)
        self.ca_dir = self.certs_dir / 'ca'
        self.broker_dir = self.certs_dir / 'broker'
        self.devices_dir = self.certs_dir / 'devices'
        self.clients_dir = self.certs_dir / 'clients'

        # Create directories
        for directory in [self.ca_dir, self.broker_dir, self.devices_dir, self.clients_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        self.ca_key = None
        self.ca_cert = None

    def generate_private_key(self, key_size=2048):
        """Generate RSA private key."""
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )

    def save_private_key(self, key, path, password=None):
        """Save private key to file."""
        encryption = serialization.NoEncryption()
        if password:
            encryption = serialization.BestAvailableEncryption(password.encode())

        with open(path, 'wb') as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=encryption
            ))
        print(f"✓ Private key saved: {path}")

    def save_certificate(self, cert, path):
        """Save certificate to file."""
        with open(path, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        print(f"✓ Certificate saved: {path}")

    def create_ca_certificate(self):
        """Create self-signed CA certificate."""
        print("\n[1/4] Generating Certificate Authority...")

        # Generate CA private key
        self.ca_key = self.generate_private_key(key_size=4096)
        ca_key_path = self.ca_dir / 'ca.key'
        self.save_private_key(self.ca_key, ca_key_path)

        # Create CA certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "FI"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Uusimaa"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Helsinki"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SmartHome IoT Test CA"),
            x509.NameAttribute(NameOID.COMMON_NAME, "SmartHome Root CA"),
        ])

        self.ca_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            self.ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=3650)  # 10 years
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=0),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                key_encipherment=False,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(self.ca_key.public_key()),
            critical=False,
        ).sign(self.ca_key, hashes.SHA256(), default_backend())

        ca_cert_path = self.ca_dir / 'ca.crt'
        self.save_certificate(self.ca_cert, ca_cert_path)

    def load_ca(self):
        """Load existing CA certificate and key."""
        ca_key_path = self.ca_dir / 'ca.key'
        ca_cert_path = self.ca_dir / 'ca.crt'

        if not ca_key_path.exists() or not ca_cert_path.exists():
            raise FileNotFoundError("CA certificate or key not found. Run create_ca_certificate first.")

        with open(ca_key_path, 'rb') as f:
            self.ca_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )

        with open(ca_cert_path, 'rb') as f:
            self.ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

    def sign_certificate(self, csr_key, common_name, dns_names=None, validity_days=365, is_server=False):
        """Sign a certificate using the CA."""
        if not self.ca_key or not self.ca_cert:
            self.load_ca()

        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "FI"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Uusimaa"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Helsinki"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SmartHome IoT"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        builder = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.ca_cert.subject
        ).public_key(
            csr_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=validity_days)
        )

        # Add Subject Alternative Names
        if dns_names:
            san_list = [x509.DNSName(name) for name in dns_names]
            builder = builder.add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False,
            )

        # Key usage
        if is_server:
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            ).add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                ]),
                critical=False,
            )
        else:
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            ).add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                ]),
                critical=False,
            )

        # Add basic constraints
        builder = builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )

        cert = builder.sign(self.ca_key, hashes.SHA256(), default_backend())
        return cert

    def create_broker_certificate(self):
        """Create MQTT broker certificate."""
        print("\n[2/4] Generating MQTT Broker certificate...")

        broker_key = self.generate_private_key()
        broker_key_path = self.broker_dir / 'broker.key'
        self.save_private_key(broker_key, broker_key_path)

        broker_cert = self.sign_certificate(
            broker_key,
            common_name="mosquitto",
            dns_names=["mosquitto", "localhost", "127.0.0.1"],
            validity_days=365,
            is_server=True
        )

        broker_cert_path = self.broker_dir / 'broker.crt'
        self.save_certificate(broker_cert, broker_cert_path)

    def create_device_certificate(self, device_id):
        """Create device certificate."""
        device_key = self.generate_private_key()
        device_key_path = self.devices_dir / f'{device_id}.key'
        self.save_private_key(device_key, device_key_path)

        device_cert = self.sign_certificate(
            device_key,
            common_name=device_id,
            validity_days=365,
            is_server=False
        )

        device_cert_path = self.devices_dir / f'{device_id}.crt'
        self.save_certificate(device_cert, device_cert_path)

    def create_client_certificate(self, client_id):
        """Create client certificate."""
        client_key = self.generate_private_key()
        client_key_path = self.clients_dir / f'{client_id}.key'
        self.save_private_key(client_key, client_key_path)

        client_cert = self.sign_certificate(
            client_key,
            common_name=client_id,
            validity_days=365,
            is_server=False
        )

        client_cert_path = self.clients_dir / f'{client_id}.crt'
        self.save_certificate(client_cert, client_cert_path)


def main():
    """Generate all certificates for the test environment."""
    print("=" * 60)
    print("SmartHome IoT Test Certificate Generator")
    print("=" * 60)

    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    certs_dir = project_root / 'certs'

    ca = CertificateAuthority(certs_dir)

    # Create CA
    ca.create_ca_certificate()

    # Create broker certificate
    ca.create_broker_certificate()

    # Create device certificates
    print("\n[3/4] Generating device certificates...")
    device_ids = [
        'device001',
        'device002',
        'device003',
        'light-living-room',
        'thermostat-bedroom',
        'sensor-kitchen'
    ]
    for device_id in device_ids:
        ca.create_device_certificate(device_id)

    # Create client certificates
    print("\n[4/4] Generating client certificates...")
    client_ids = [
        'test-client',
        'admin-client',
        'monitoring-client'
    ]
    for client_id in client_ids:
        ca.create_client_certificate(client_id)

    print("\n" + "=" * 60)
    print("✓ Certificate generation completed successfully!")
    print("=" * 60)
    print(f"\nCertificates location: {certs_dir}")
    print("\nGenerated certificates:")
    print(f"  CA:      {ca.ca_dir}/ca.crt")
    print(f"  Broker:  {ca.broker_dir}/broker.crt")
    print(f"  Devices: {len(device_ids)} certificates in {ca.devices_dir}/")
    print(f"  Clients: {len(client_ids)} certificates in {ca.clients_dir}/")
    print("\n⚠️  WARNING: In production, keep private keys secure and never commit them!")
    print("=" * 60)


if __name__ == '__main__':
    main()
