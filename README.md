# SmartHome IoT Test Automation Framework

[![CI/CD Pipeline](https://github.com/mankin3n/MQTTest/actions/workflows/ci.yml/badge.svg)](https://github.com/mankin3n/MQTTest/actions)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Robot Framework](https://img.shields.io/badge/Robot%20Framework-7.0-green.svg)](https://robotframework.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Enterprise-grade test automation framework for IoT platforms with MQTT messaging, REST APIs, and certificate-based security (mTLS). Built with Robot Framework and designed for production-scale testing.

## Features

### Core Capabilities
- **MQTT Testing** - Full pub/sub testing with QoS 0, 1, 2 support
- **mTLS Authentication** - Certificate-based device authentication
- **REST API Testing** - Comprehensive API testing with JWT authentication
- **Performance Testing** - Response time and throughput validation
- **CI/CD Integration** - GitHub Actions pipeline with parallel execution
- **Custom Libraries** - Purpose-built Python libraries for IoT testing
- **Docker Support** - Containerized test environment

### Test Coverage
- ✅ Device Management API (CRUD operations)
- ✅ MQTT Publish/Subscribe (all QoS levels)
- ✅ Authentication & Authorization (JWT, mTLS)
- ✅ Automation Rules Engine
- ✅ Certificate Lifecycle Management
- ✅ End-to-End Integration Scenarios
- ✅ Performance & Load Testing
- ✅ Security & Negative Testing

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### ⚡ Enhanced CLI (Recommended)

We now have a modern, interactive CLI with beautiful terminal UI:

```bash
# Interactive mode - just run and select from menu
python3 cli_enhanced.py

# Or use direct commands
python3 cli_enhanced.py setup
python3 cli_enhanced.py run --suite smoke
python3 cli_enhanced.py services
```

**Features:**
- 🎨 Beautiful interactive menus
- 📊 Rich progress indicators
- 🔍 Tree view of test structure
- ✨ One-click report opening
- 🚀 Quick start wizard

See [CLI_README.md](CLI_README.md) for full documentation.

### Installation

```bash
# Clone the repository
git clone https://github.com/mankin3n/MQTTest.git
cd MQTTest

# Run setup (installs dependencies & generates certificates)
python3 cli_enhanced.py setup
# or use the original CLI:
python3 cli.py setup

# Start services (MQTT broker & Mock API)
python3 cli_enhanced.py services
# or: python3 cli.py services

# Run smoke tests
python3 cli.py run --suite smoke
```

## Project Structure

```
.
├── cli.py                      # CLI interface for test execution
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Service orchestration
│
├── config/                     # Environment configurations
│   ├── __init__.py
│   └── environments/
│       ├── dev.yaml           # Development config
│       └── ci.yaml            # CI/CD config
│
├── libraries/                  # Custom test libraries
│   ├── api/                   # REST API library
│   │   ├── __init__.py
│   │   └── APILibrary.py      # HTTP operations, JWT auth
│   ├── mqtt/                  # MQTT library
│   │   ├── __init__.py
│   │   └── MQTTLibrary.py     # MQTT pub/sub, mTLS
│   └── utils/                 # Utility libraries
│       ├── __init__.py
│       └── TestDataFactory.py # Test data generation
│
├── resources/                  # Robot Framework resources
│   ├── common.robot           # Common keywords & setup
│   ├── device_management.robot # Device operations
│   └── automation_rules.robot  # Automation testing
│
├── tests/                      # Test suites
│   ├── api/
│   │   └── test_device_api.robot        # API tests (TC001-TC010)
│   ├── mqtt/
│   │   └── test_mqtt_pubsub.robot       # MQTT tests (TC011-TC020)
│   ├── security/
│   │   └── test_authentication.robot    # Security tests (TC021-TC030)
│   └── integration/
│       └── test_end_to_end.robot        # Integration tests (TC031-TC040)
│
├── certs/                      # Test certificates
│   ├── ca/                    # Certificate Authority
│   ├── broker/                # MQTT broker certs
│   ├── devices/               # Device certificates
│   └── clients/               # Client certificates
│
├── scripts/
│   ├── generate_certs.py      # Certificate generation
│   ├── cert_manager.sh        # Certificate management
│   └── setup.sh              # Environment setup
│
├── docker/
│   ├── mosquitto.conf         # MQTT broker config (TLS)
│   ├── mock-api.py           # Mock REST API server
│   └── Dockerfile.mock-api    # API Docker image
│
└── .github/
    └── workflows/
        └── ci.yml            # GitHub Actions pipeline
```

## Usage

### CLI Commands

The framework includes a comprehensive CLI for test execution:

```bash
# Setup environment
python3 cli.py setup                    # Install deps & generate certs
python3 cli.py setup --skip-deps       # Skip dependency installation

# Manage services
python3 cli.py services                 # Start Docker services
python3 cli.py stop                     # Stop services
python3 cli.py status                   # Check service status

# Run tests
python3 cli.py run --suite smoke        # Run smoke tests
python3 cli.py run --suite api          # Run API tests
python3 cli.py run --suite mqtt         # Run MQTT tests
python3 cli.py run --suite security     # Run security tests
python3 cli.py run --suite integration  # Run integration tests
python3 cli.py run --suite all          # Run all tests

# Advanced options
python3 cli.py run --suite api --parallel  # Parallel execution
python3 cli.py run --tags positive         # Run specific tags
python3 cli.py run --env ci               # Use CI config
python3 cli.py run --verbose              # Verbose output
python3 cli.py run --dry-run              # Preview without running

# Utilities
python3 cli.py list-tests               # List all tests
python3 cli.py certs                    # Show certificate status
python3 cli.py clean                    # Clean reports
python3 cli.py info                     # Show project info
```

### Running Tests Manually

```bash
# Activate virtual environment (if used)
source venv/bin/activate

# Run specific test file
robot --variable ENV:dev tests/api/test_device_api.robot

# Run tests with tags
robot --include smoke --variable ENV:dev tests/

# Run tests in parallel
pabot --processes 4 --variable ENV:dev tests/

# Generate detailed report
robot --loglevel DEBUG --outputdir reports tests/
```

### Docker-Based Testing

```bash
# Build and run tests in Docker
docker-compose up -d                    # Start services
docker-compose --profile test up        # Run tests in container
docker-compose down                     # Stop all services

# Run specific test suite in Docker
docker-compose run test-runner robot --include api tests/
```

## Certificate Management

The framework uses mTLS for MQTT broker authentication:

### Generate Certificates

```bash
# Using Python script
python3 scripts/generate_certs.py

# Using shell script
./scripts/cert_manager.sh generate
```

### Certificate Structure

```
certs/
├── ca/
│   ├── ca.crt              # Root CA certificate
│   └── ca.key              # CA private key
├── broker/
│   ├── broker.crt          # Mosquitto broker certificate
│   └── broker.key          # Broker private key
├── devices/
│   ├── device001.crt       # Device certificates
│   ├── device001.key
│   └── ...
└── clients/
    ├── test-client.crt     # Test client certificate
    └── test-client.key
```

### Certificate Operations

```bash
# List all certificates
./scripts/cert_manager.sh list

# Verify certificate
./scripts/cert_manager.sh verify certs/ca/ca.crt

# Check expiry dates
./scripts/cert_manager.sh expiry

# Clean and regenerate
./scripts/cert_manager.sh clean
python3 scripts/generate_certs.py
```

## Test Cases

### API Tests (tests/api/test_device_api.robot)
- `TC001`: Register new light device
- `TC002`: Register thermostat device
- `TC003`: Get device status
- `TC004`: Update device configuration
- `TC005`: Delete device
- `TC006`: Authentication required
- `TC007`: Non-existent device returns 404
- `TC008`: Invalid data validation
- `TC009`: Batch device registration
- `TC010`: Performance verification

### MQTT Tests (tests/mqtt/test_mqtt_pubsub.robot)
- `TC011-TC013`: QoS 0, 1, 2 testing
- `TC014`: Wildcard topic subscription
- `TC015`: Retained messages
- `TC016`: Device telemetry publishing
- `TC017`: Device command handling
- `TC018`: Multiple subscriptions
- `TC019`: Unsubscribe functionality
- `TC020`: Metrics tracking

### Security Tests (tests/security/test_authentication.robot)
- `TC021-TC026`: JWT authentication
- `TC027-TC029`: Certificate-based auth
- `TC030`: Failed auth tracking

### Integration Tests (tests/integration/test_end_to_end.robot)
- `TC031`: Complete device lifecycle
- `TC032`: Command and response flow
- `TC033`: Automation rule end-to-end
- `TC034`: Multi-device telemetry
- `TC035`: Certificate provisioning
- `TC036-TC037`: Performance testing
- `TC038`: Multiple automation rules
- `TC039`: Status monitoring
- `TC040`: System health check

## Architecture

### MQTT Broker (Mosquitto)
- **Port**: 8883 (MQTT over TLS)
- **WebSocket**: 9001 (WSS)
- **Authentication**: Client certificates (mTLS)
- **Configuration**: `docker/mosquitto.conf`

### Mock REST API
- **Port**: 8000
- **Endpoints**:
  - `POST /api/v1/devices` - Register device
  - `GET /api/v1/devices/{id}` - Get device
  - `PUT /api/v1/devices/{id}` - Update device
  - `DELETE /api/v1/devices/{id}` - Delete device
  - `POST /api/v1/automation-rules` - Create rule
  - `POST /api/v1/certificates/provision` - Provision cert
  - `GET /health` - Health check

### MQTT Topics
```
home/{device_id}/telemetry      # Device → Cloud (telemetry data)
home/{device_id}/command        # Cloud → Device (commands)
home/{device_id}/status         # Device status updates
home/events/automation          # Automation rule triggers
```

## CI/CD Pipeline

GitHub Actions workflow includes:

1. **Code Quality** - Linting (Black, Flake8)
2. **Certificate Setup** - Auto-generate test certs
3. **Parallel Test Execution**:
   - API Tests
   - MQTT Tests
   - Security Tests
   - Integration Tests
   - Smoke Tests
4. **Report Generation** - Merged test results
5. **Artifact Upload** - Test reports and logs

### Running in CI

The pipeline automatically runs on:
- Push to `main` or `develop`
- Pull requests
- Manual trigger (`workflow_dispatch`)

## Configuration

### Environment Files

Edit `config/environments/dev.yaml` or `config/environments/ci.yaml`:

```yaml
api:
  base_url: http://localhost:8000
  timeout: 30

mqtt:
  broker_host: localhost
  broker_port: 8883
  ca_cert: certs/ca/ca.crt
  client_cert: certs/clients/test-client.crt
  client_key: certs/clients/test-client.key

auth:
  admin_username: admin@smarthome.local
  jwt_secret: your-secret-key
```

### Switching Environments

```bash
# Development
python3 cli.py run --env dev

# CI/CD
python3 cli.py run --env ci
```

## Development

### Adding New Tests

1. Create test file in appropriate directory:
   ```robot
   *** Settings ***
   Resource    ../../resources/common.robot

   *** Test Cases ***
   My New Test
       [Tags]    smoke
       # Test steps here
   ```

2. Run the test:
   ```bash
   python3 cli.py run --tags smoke
   ```

### Creating Custom Keywords

Add keywords to `resources/*.robot` files:

```robot
*** Keywords ***
My Custom Keyword
    [Arguments]    ${arg1}    ${arg2}
    Log    Processing ${arg1} and ${arg2}
    # Implementation
```

### Extending Python Libraries

Modify libraries in `libraries/*/` and use the `@keyword` decorator:

```python
from robot.api.deco import keyword

@keyword("My Custom Keyword")
def my_custom_keyword(self, param):
    # Implementation
    pass
```

## Troubleshooting

### Common Issues

**Certificate errors:**
```bash
# Regenerate certificates
python3 cli.py setup
```

**MQTT connection fails:**
```bash
# Check broker is running
docker-compose ps mosquitto

# Check logs
docker-compose logs mosquitto
```

**API not responding:**
```bash
# Check API health
curl http://localhost:8000/health

# Restart services
docker-compose restart mock-api
```

### Debug Mode

Run tests with verbose logging:
```bash
python3 cli.py run --suite api --verbose
```

View detailed logs:
```bash
# Robot Framework logs
cat reports/*/log.html

# MQTT broker logs
docker-compose logs -f mosquitto

# API logs
docker-compose logs -f mock-api
```

## Performance Metrics

The framework tracks:
- API response times
- MQTT message latency
- Message throughput
- Connection stability
- Test execution time

Access metrics via keywords:
```robot
${api_metrics}=    Get API Metrics
${mqtt_metrics}=   Get MQTT Metrics
```

## Best Practices

1. **Always run smoke tests** before committing
2. **Use tags** for test organization
3. **Generate fresh certificates** for security tests
4. **Clean up resources** in test teardown
5. **Use parallel execution** for faster CI
6. **Monitor performance metrics** for regressions
7. **Keep certificates secure** (don't commit private keys in production)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Robot Framework community
- Eclipse Mosquitto project
- Paho MQTT Python client
- Flask web framework

## Contact

For questions or support:
- Create an issue on GitHub
- Email: your.email@example.com

---

**Built with ❤️ for robust IoT testing**
